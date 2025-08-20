from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model that provides created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Note(TimeStampedModel):
    """Note model storing a user's note with title and content."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        help_text="Owner of the note",
    )
    title = models.CharField(max_length=255, help_text="Title of the note")
    content = models.TextField(blank=True, help_text="Content of the note")
    is_archived = models.BooleanField(default=False, help_text="Archived flag")

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_archived"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} (#{self.pk})"
