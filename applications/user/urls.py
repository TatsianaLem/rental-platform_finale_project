from django.urls import path
from applications.user.views import RegisterAPIView, LoginView
from .views import LogoutView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

