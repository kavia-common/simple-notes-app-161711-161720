from django.contrib.auth import get_user_model, login as django_login, logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Note
from .serializers import (
    NoteSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)

User = get_user_model()


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="get",
    operation_summary="Health check",
    operation_description="Returns a simple health status message.",
    responses={200: openapi.Response("Health response", schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
    ))},
    tags=["health"],
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    """Simple health endpoint to verify the server is up."""
    return Response({"message": "Server is up!"})


class IsOwner(permissions.BasePermission):
    """Permission that allows only owners of a Note to access or modify it."""

    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "owner_id", None) == getattr(request.user, "id", None)


class NoteViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet for CRUD operations on notes owned by the authenticated user."""
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = Note.objects.filter(owner=self.request.user)
        archived_param = self.request.query_params.get("archived")
        if archived_param is not None:
            if archived_param.lower() in ("1", "true", "yes"):
                qs = qs.filter(is_archived=True)
            elif archived_param.lower() in ("0", "false", "no"):
                qs = qs.filter(is_archived=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "archived",
                openapi.IN_QUERY,
                description="Filter by archived status (true/false)",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        operation_summary="List notes",
        tags=["notes"],
    )
    def list(self, request, *args, **kwargs):
        """List notes for the authenticated user, optionally filtered by archived flag."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create note", tags=["notes"])
    def create(self, request, *args, **kwargs):
        """Create a new note for the authenticated user."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Retrieve note", tags=["notes"])
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific note owned by the user."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update note", tags=["notes"])
    def update(self, request, *args, **kwargs):
        """Update a specific note."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Partial update note", tags=["notes"])
    def partial_update(self, request, *args, **kwargs):
        """Partially update a specific note."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete note", tags=["notes"])
    def destroy(self, request, *args, **kwargs):
        """Delete a note."""
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="archive", permission_classes=[permissions.IsAuthenticated, IsOwner])
    @swagger_auto_schema(operation_summary="Archive a note", tags=["notes"])
    def archive(self, request, pk=None):
        """Archive a note."""
        note = self.get_object()
        note.is_archived = True
        note.save(update_fields=["is_archived", "updated_at"])
        serializer = self.get_serializer(note)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="unarchive", permission_classes=[permissions.IsAuthenticated, IsOwner])
    @swagger_auto_schema(operation_summary="Unarchive a note", tags=["notes"])
    def unarchive(self, request, pk=None):
        """Unarchive a note."""
        note = self.get_object()
        note.is_archived = False
        note.save(update_fields=["is_archived", "updated_at"])
        serializer = self.get_serializer(note)
        return Response(serializer.data)


# Authentication endpoints

# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Register user",
    operation_description="Create a new user account.",
    request_body=RegisterSerializer,
    responses={201: UserSerializer},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def register(request):
    """Register a new user with username, email and password."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Login",
    operation_description="Authenticate a user using session authentication.",
    request_body=LoginSerializer,
    responses={200: UserSerializer},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def login(request):
    """Login a user and establish a session."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        django_login(request, user)
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Logout",
    operation_description="Logout the current user (session based).",
    responses={204: "No Content"},
    tags=["auth"],
)
@api_view(["POST"])
def logout(request):
    """Logout the current user."""
    django_logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="get",
    operation_summary="Get current user",
    operation_description="Retrieve current logged-in user profile.",
    responses={200: UserSerializer},
    tags=["auth"],
)
@api_view(["GET"])
def me(request):
    """Return the current authenticated user's profile."""
    return Response(UserSerializer(request.user).data)
