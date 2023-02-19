from rest_framework import routers
from .views import ProductoViewSet, ClientViewSet, VentaViewSet, VentaProductoViewSet,UserViewSet, LogoutView , LoginView, UserRegisterView, EmailPasswordReset, ResetPasswordAPI
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path

router  = routers.DefaultRouter()
router.register('producto', ProductoViewSet)
router.register('cliente', ClientViewSet)
router.register('venta', VentaViewSet)
router.register('ventaproducto',VentaProductoViewSet)
router.register('user', UserViewSet)

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', UserRegisterView.as_view(), name='register'),
    path("email-password/", EmailPasswordReset.as_view(), name="request-password-reset"),
    path("reset-password/<str:encoded_pk>/<str:token>/", ResetPasswordAPI.as_view(), name="reset-password",
    ),
] + router.urls
