from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Note

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Username already exists"))
        return value

    def create(self, validated_data):
        # Ensure password gets hashed
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError(_("Invalid credentials"), code="authorization")
        attrs["user"] = user
        return attrs


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model with basic validation."""
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "content", "is_archived", "created_at", "updated_at", "owner"]
        read_only_fields = ["id", "created_at", "updated_at", "owner"]

    def validate_title(self, value: str):
        if not value or not value.strip():
            raise serializers.ValidationError(_("Title cannot be empty"))
        return value.strip()
