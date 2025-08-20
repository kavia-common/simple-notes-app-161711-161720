from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import health, NoteViewSet, register, login, logout, me

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="note")

urlpatterns = [
    path("health/", health, name="Health"),
    path("auth/register/", register, name="auth-register"),
    path("auth/login/", login, name="auth-login"),
    path("auth/logout/", logout, name="auth-logout"),
    path("auth/me/", me, name="auth-me"),
    path("", include(router.urls)),
]
