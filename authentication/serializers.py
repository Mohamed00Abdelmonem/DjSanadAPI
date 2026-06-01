"""
Serializers for authentication endpoints.
Handles validation and data transformation for all auth operations.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils import get_tokens_for_user
from profiles.models import Profile
from profiles.serializers import ProfileResponseSerializer

User = get_user_model()


class ObjectIdField(serializers.Field):
    """Custom field to handle MongoDB ObjectId serialization."""
    
    def to_representation(self, value):
        """Convert ObjectId to string."""
        return str(value) if value else None
    
    def to_internal_value(self, data):
        """Convert string to ObjectId."""
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    id = ObjectIdField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'date_of_birth', 'is_active', 'is_staff', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_staff')


class MeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating authenticated user's profile fields."""

    class Meta:
        model = User
        fields = ('name', 'date_of_birth')
        extra_kwargs = {
            'name': {'required': False},
            'date_of_birth': {'required': False},
        }

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                'Provide at least one of: name, date_of_birth.'
            )
        return attrs


class MeResponseSerializer(UserSerializer):
    """Serializer for authenticated user details with optional profile data."""

    profile = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('profile',)

    def get_profile(self, obj):
        profile = Profile.objects.filter(user=obj).first()
        if not profile:
            print("No profile found for user:", obj.email)  # Debug statement
            return {}
        return ProfileResponseSerializer(profile).data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates and creates a new user account.
    """

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    date_of_birth = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'date_of_birth', 'password', 'password_confirm')

    def validate(self, data):
        """Validate that passwords match and password is strong."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password': "Password fields didn't match."}
            )

        # Validate password strength using Django's validators
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError(
                {'password': list(e.messages)}
            )

        return data

    def validate_email(self, value):
        """Check that email is not already used."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        """Create new user account."""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            date_of_birth=validated_data['date_of_birth'],
            password=password
        )

        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification using 8-character token."""

    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=8, min_length=8)


class LoginSerializer(TokenObtainPairSerializer):
    """
    Custom login serializer using JWT.
    Extends TokenObtainPairSerializer to use email instead of username.
    """

    username_field = User.USERNAME_FIELD  # Uses email from custom user model

    def validate(self, attrs):
        """Validate login credentials and check if user is active."""
        data = super().validate(attrs)
        # Check if user is active
        if not self.user.is_active:
            raise serializers.ValidationError(
                {'detail': "This account is not active. Please verify your email."}
            )

        # Add user data to response
        data['user'] = UserSerializer(self.user).data

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users)."""

    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """Validate passwords match and are strong."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password': "Password fields didn't match."}
            )

        # Validate password strength
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )

        return data

    def validate_old_password(self, value):
        """Check that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {'old_password': "Old password is incorrect."}
            )
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Ensure the provided email belongs to an existing user."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset with email and token."""

    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=8, min_length=8)
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """Validate passwords match and are strong."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password': "Password fields didn't match."}
            )

        # Validate password strength
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )

        return data


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google sign-in using an ID token."""

    id_token = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh."""

    refresh = serializers.CharField(required=True)
