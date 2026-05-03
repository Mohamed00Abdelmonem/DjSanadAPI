"""
Utility functions for authentication and token management.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class EmailTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for password reset.
    Generates secure tokens that expire after a certain period.
    """

    def _make_hash_value(self, user, timestamp):
        """Include user password_changed_at for token invalidation on password change."""
        return f"{user.pk}{user.email}{timestamp}{user.password_changed_at}"


# Global token generator
email_token_generator = EmailTokenGenerator()


def generate_email_verification_token():
    """
    Generate a random 8-character alphanumeric verification token.
    
    Returns:
        String token (8 characters)
    """
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(8))
    return token


def verify_email_verification_token(token, email):
    """
    Verify email verification token and return user if valid.

    Args:
        token: Token string (8 characters)
        email: User email

    Returns:
        User instance or None if token is invalid or expired
    """
    try:
        from users.models import User

        user = User.objects.get(email=email)

        # Check if token matches and hasn't expired
        if user.email_verification_token == token:
            if user.email_verification_token_expiry and user.email_verification_token_expiry > timezone.now():
                return user
        
        return None
    except User.DoesNotExist:
        return None


def generate_password_reset_token(user):
    """
    Generate a secure password reset token for user.

    Args:
        user: User instance

    Returns:
        Tuple of (uidb64, token)
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    return uidb64, token


def verify_password_reset_token(uidb64, token):
    """
    Verify password reset token and return user if valid.

    Args:
        uidb64: Base64 encoded user ID
        token: Token string

    Returns:
        User instance or None if token is invalid
    """
    try:
        from users.models import User

        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Check token validity and expiry
        if email_token_generator.check_token(user, token):
            return user
        return None
    except (ValueError, User.DoesNotExist):
        return None


def send_email_verification(user):
    """
    Send email verification token to user.
    Generates a random 8-character token and sends it via email.

    Args:
        user: User instance

    Returns:
        Boolean indicating success
    """
    try:
        # Generate random 8-character token
        token = generate_email_verification_token()
        
        # Store token with 24-hour expiry
        user.email_verification_token = token
        user.email_verification_token_expiry = timezone.now() + timedelta(hours=24)
        user.save(update_fields=['email_verification_token', 'email_verification_token_expiry'])

        context = {
            'user': user,
            'token': token,
        }

        # Try to render HTML email template, fall back to plain text
        try:
            html_message = render_to_string(
                'authentication/emails/verify_email.html',
                context
            )
        except Exception:
            html_message = f"""
            <h2>Welcome to Sanad, {user.name}!</h2>
            <p>Please verify your email using the code below:</p>
            <h1 style="font-size: 36px; letter-spacing: 10px; font-weight: bold;">{token}</h1>
            <p>This code will expire in 24 hours.</p>
            <p>If you did not create this account, please ignore this email.</p>
            """

        subject = 'Verify Your Email - Sanad'
        message = f"""
Welcome to Sanad, {user.name}!

Please verify your email using the code below:

{token}

This code will expire in 24 hours.

If you did not create this account, please ignore this email.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email verification token sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email verification to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user):
    """
    Send password reset link to user.

    Args:
        user: User instance

    Returns:
        Boolean indicating success
    """
    try:
        uidb64, token = generate_password_reset_token(user)
        reset_url = f"{settings.FRONTEND_RESET_PASSWORD_URL}?uid={uidb64}&token={token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Try to render HTML email template, fall back to plain text
        try:
            html_message = render_to_string(
                'authentication/emails/reset_password.html',
                context
            )
        except Exception:
            html_message = f"""
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            """

        subject = 'Reset Your Password - Sanad'
        message = f"""
        Reset your password by clicking the link below:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, ignore this email.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def get_tokens_for_user(user):
    """
    Get both access and refresh tokens for user.

    Args:
        user: User instance

    Returns:
        Dictionary with access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
