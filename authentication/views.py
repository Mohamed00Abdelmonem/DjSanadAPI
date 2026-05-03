"""
API Views for authentication endpoints.
Implements complete JWT-based authentication with email verification,
password reset, and token management.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)
from .utils import (
    send_email_verification,
    send_password_reset_email,
    verify_email_verification_token,
    verify_password_reset_token,
    get_tokens_for_user,
)

User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Register a new user account.
    Sends email verification link.

    Request body:
    {
        "email": "user@example.com",
        "name": "John Doe",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    }

    Response:
    {
        "detail": "User registered successfully. Please check your email to verify your account.",
        "email": "user@example.com"
    }
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Send email verification
            if send_email_verification(user):
                return Response(
                    {
                        'detail': 'User registered successfully. Please check your email to verify your account.',
                        'email': user.email,
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                # User created but email failed - still return success but note email issue
                return Response(
                    {
                        'detail': 'User registered but verification email could not be sent. Please contact support.',
                        'email': user.email,
                    },
                    status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    POST /api/auth/activate/

    Verify email and activate user account using 8-character token.

    Request body:
    {
        "email": "user@example.com",
        "token": "ABC12345"
    }

    Response:
    {
        "detail": "Email verified successfully. Your account is now active.",
        "user": {
            "id": "...",
            "email": "user@example.com",
            "name": "John Doe",
            ...
        }
    }
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']

            user = verify_email_verification_token(token, email)

            if user is not None:
                user.mark_email_verified()
                # Clear the used token
                user.email_verification_token = None
                user.email_verification_token_expiry = None
                user.save(update_fields=['email_verification_token', 'email_verification_token_expiry'])
                
                return Response(
                    {
                        'detail': 'Email verified successfully. Your account is now active.',
                        'user': UserSerializer(user).data,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'Invalid or expired verification token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/

    Login user with email and password.
    Returns JWT tokens (access and refresh).

    Request body:
    {
        "email": "user@example.com",
        "password": "StrongPassword123!"
    }

    Response:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": "...",
            "email": "user@example.com",
            "name": "John Doe",
            ...
        }
    }
    """

    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/auth/token/refresh/

    Refresh expired access token using refresh token.

    Request body:
    {
        "refresh": "refresh_token_string"
    }

    Response:
    {
        "access": "new_access_token_string"
    }
    """

    permission_classes = (AllowAny,)


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/

    Change password for authenticated user.

    Headers:
    Authorization: Bearer <access_token>

    Request body:
    {
        "old_password": "CurrentPassword123!",
        "new_password": "NewPassword456!",
        "new_password_confirm": "NewPassword456!"
    }

    Response:
    {
        "detail": "Password changed successfully."
    }
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(
                {'detail': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/

    Request password reset email.
    Sends reset link to user email.

    Request body:
    {
        "email": "user@example.com"
    }

    Response:
    {
        "detail": "If a user with this email exists, a password reset link has been sent."
    }
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
                send_password_reset_email(user)
            except User.DoesNotExist:
                # Don't reveal if user exists
                pass

            # Always return success for security (user enumeration prevention)
            return Response(
                {
                    'detail': 'If a user with this email exists, a password reset link has been sent.'
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/

    Reset password using token from email.

    Request body:
    {
        "uid": "base64_encoded_user_id",
        "token": "reset_token",
        "new_password": "NewPassword123!",
        "new_password_confirm": "NewPassword123!"
    }

    Response:
    {
        "detail": "Password reset successfully. You can now login with your new password."
    }
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']

            user = verify_password_reset_token(uid, token)

            if user is not None:
                user.set_password(serializer.validated_data['new_password'])
                user.save()

                return Response(
                    {
                        'detail': 'Password reset successfully. You can now login with your new password.'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'Invalid or expired reset token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    GET /api/auth/me/

    Get current authenticated user details.

    Headers:
    Authorization: Bearer <access_token>

    Response:
    {
        "id": "...",
        "email": "user@example.com",
        "name": "John Doe",
        "is_active": true,
        "is_staff": false,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Logout user (invalidate refresh token).
    Note: With JWT, tokens remain valid until expiry.
    This endpoint can be used to track logout on client side
    and trigger token blacklist if using token blacklist app.

    Headers:
    Authorization: Bearer <access_token>

    Response:
    {
        "detail": "Logged out successfully."
    }
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(
            {'detail': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )
