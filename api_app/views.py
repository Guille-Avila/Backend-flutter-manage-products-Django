from django.conf import settings
from rest_framework import viewsets, permissions, generics
from .models import DetailSale, Producto, Client, Sale
from .serializers import DetailSaleSerializer, ProductoSerializer, ClientSerializer, SaleSerializer, UserSerializer, EmailPasswordResetSerializer, ResetPasswordSerializer
from rest_framework import status, views, authentication
from rest_framework.response import Response
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
    
class ClientViewSet(viewsets.ModelViewSet):
  queryset = Client.objects.all()  
  permission_classes = [permissions.AllowAny]
  serializer_class = ClientSerializer



class SaleViewSet(viewsets.ModelViewSet):
  queryset = Sale.objects.all()
  permission_classes = [permissions.AllowAny]
  serializer_class = SaleSerializer

class DetailSaleViewSet(viewsets.ModelViewSet):
  queryset = DetailSale.objects.all()
  permission_classes = [permissions.AllowAny]
  serializer_class = DetailSaleSerializer



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
            return Response({'message': 'Please provide both username and password'},status=status.HTTP_400_BAD_REQUEST)
        user2 = authenticate(username=username2, password=password2)
        if not user2:
            return Response({'message': 'Usuario o Contrase??a incorrecto !!!! '},status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user2)
        # Si es correcto a??adimos a la request la informaci??n de sesi??n
        if user2:
            # para loguearse una sola vez
            # login(request, user)
            return Response({'message':'usuario y contrase??a correctos!!!!'},status=status.HTTP_200_OK)
            #return response.Response({'token': token.key}, status=status.HTTP_200_OK)

        # Si no es correcto devolvemos un error en la petici??n
        return Response(status=status.HTTP_404_NOT_FOUND)        

class LogoutView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    def post(self, request):        
        request.user.auth_token.delete()
        # Borramos de la request la informaci??n de sesi??n
        logout(request)
        # Devolvemos la respuesta al cliente
        return Response({'message':'Sessi??n Cerrada y Token Eliminado !!!!'},status=status.HTTP_200_OK)

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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

            return Response(
                {"message": f"Your password rest link: {reset_link}"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
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
        return Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )