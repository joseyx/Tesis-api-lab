from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UserViewApi, UserViewApiDetail, ProtectedView, \
    UsuarioView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('users', UserViewApi.as_view()),
    path('users/<int:id>', UserViewApiDetail.as_view()),
    path('usuario', UsuarioView.as_view()),
    path('protected', ProtectedView.as_view()),
]
