from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UserViewApi, UserViewApiDetail, ProtectedView, \
    UsuarioView, RequestPasswordResetEmail, PasswordTokenCheck, SetNewPassword

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('users', UserViewApi.as_view()),
    path('users/<int:user_id>', UserViewApiDetail.as_view()),
    path('usuario', UsuarioView.as_view()),
    path('protected', ProtectedView.as_view()),
    path('request-reset-email', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<str:uidb64>/<str:token>', PasswordTokenCheck.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPassword.as_view(), name='password-reset-complete')
]
