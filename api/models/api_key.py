from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
import secrets

from api.models.base import MerlinBaseModel

__all__ = ["ApiKey"]


class ApiKey(MerlinBaseModel):
    """API Key for service account authentication.
    
    Keys are stored hashed (similar to passwords) for security.
    The plain key is only shown once when created.
    """
    user = models.ForeignKey(
        "api.User",
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="User",
        help_text="User account associated with this API key",
    )
    name = models.CharField(
        max_length=256,
        verbose_name="Key Name",
        help_text="Descriptive name for this API key (e.g., 'Metabase Integration')",
    )
    key_prefix = models.CharField(
        max_length=12,
        verbose_name="Key Prefix",
        help_text="First 12 characters of the key (for identification)",
        editable=False,
    )
    key_hash = models.CharField(
        max_length=128,
        verbose_name="Key Hash",
        help_text="Hashed version of the API key",
        editable=False,
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Used",
        help_text="Timestamp of last successful authentication with this key",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this API key is active and can be used",
    )

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ("-date_created",)
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...) - {self.user.email}"

    def set_key(self, key: str):
        """Set the API key (hashes it and sets prefix)."""
        self.key_hash = make_password(key)
        self.key_prefix = key[:12] if len(key) >= 12 else key

    def verify_key(self, key: str) -> bool:
        """Verify if the provided key matches this API key."""
        if not self.is_active:
            return False
        return check_password(key, self.key_hash)

    def record_usage(self):
        """Record that this key was used (updates last_used timestamp)."""
        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    @classmethod
    def generate_key(cls) -> str:
        """Generate a new secure API key.
        
        Format: pk_live_<random_secret>
        """
        random_part = secrets.token_urlsafe(32)  # 32 bytes = 43 chars in base64
        return f"pk_live_{random_part}"

