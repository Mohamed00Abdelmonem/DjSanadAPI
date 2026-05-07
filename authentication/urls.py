"""
URL configuration for authentication endpoints.
"""

from django.urls import path
from .views import (
    RegisterView,
    EmailVerificationView,
    LoginView,
    RefreshTokenView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
    GoogleAuthView,
    MeView,
    LogoutView,
)

app_name = 'authentication'

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', EmailVerificationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('google/', GoogleAuthView.as_view(), name='google_auth'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
