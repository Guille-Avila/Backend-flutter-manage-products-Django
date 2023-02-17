from django.conf import settings
from rest_framework import viewsets, permissions, generics
from .models import Producto, Client, Venta, VentaProducto
from .serializers import ProductoSerializer, ClientSerializer, VentaSerializer, VentaProductoSerializer, UserSerializer, EmailPasswordResetSerializer, ResetPasswordSerializer
from rest_framework import status, views, response
from rest_framework import authentication
from django.contrib.auth.models import User
from django.contrib.auth import logout ,authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [authentication.BasicAuthentication]
    
class ClientViewSet(viewsets.ModelViewSet):
  queryset = Client.objects.all()  
  permission_classes = [permissions.AllowAny]
  serializer_class = ClientSerializer

class VentaViewSet(viewsets.ModelViewSet):
  queryset = Venta.objects.all()
  permission_classes = [permissions.IsAuthenticated]
  authentication_classes = [authentication.TokenAuthentication,]
  serializer_class = VentaSerializer

class VentaProductoViewSet(viewsets.ModelViewSet):
  queryset = VentaProducto.objects.all()
  permission_classes = [permissions.AllowAny]
  serializer_class = VentaProductoSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser,]
    authentication_classes = [authentication.BasicAuthentication,]

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        # Recuperamos las credenciales y autenticamos al usuario
        username2= request.data.get('username', None)
        password2 = request.data.get('password', None)
        if username2 is None or password2 is None:
            return response.Response({'message': 'Please provide both username and password'},status=status.HTTP_400_BAD_REQUEST)
        user2 = authenticate(username=username2, password=password2)
        if not user2:
            return response.Response({'message': 'Usuario o Contraseña incorrecto !!!! '},status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user2)
        # Si es correcto añadimos a la request la información de sesión
        if user2:
            # para loguearse una sola vez
            # login(request, user)
            return response.Response({'message':'usuario y contraseña correctos!!!!'},status=status.HTTP_200_OK)
            #return response.Response({'token': token.key}, status=status.HTTP_200_OK)

        # Si no es correcto devolvemos un error en la petición
        return response.Response(status=status.HTTP_404_NOT_FOUND)        

class LogoutView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    def post(self, request):        
        request.user.auth_token.delete()
        # Borramos de la request la información de sesión
        logout(request)
        # Devolvemos la respuesta al cliente
        return response.Response({'message':'Sessión Cerrada y Token Eliminado !!!!'},status=status.HTTP_200_OK)

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['GET'])
def check_email(request):
    email = request.query_params.get('email', '')
    users = User.objects.filter(email=email)
    exists = True if users else False
    return response.Response({'exists': exists})

class EmailPasswordReset(generics.GenericAPIView):
    serializer_class = EmailPasswordResetSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.filter(email=email).first()
        
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            # reset_url = reverse(
            #     "reset-password",
            #     kwargs={"encoded_pk": encoded_pk, "token": token},
            # )
            reset_link = f"http://localhost:8080/restart-password/?pk={encoded_pk}&token={token}"

            # send the rest_link as mail to the user.
            html_message = render_to_string('reset_password_email.html', {'reset_link': reset_link})
            text_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                'Reset password app Flutter',
                text_message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            return response.Response(
                {"message": f"Your password rest link: {reset_link}"},
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ResetPasswordAPI(generics.GenericAPIView):

    serializer_class = ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return response.Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )