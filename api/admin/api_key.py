"""Admin interface for API Key management."""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages

from api.models import ApiKey

__all__ = ["ApiKeyAdmin"]


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    """Admin interface for managing API keys."""
    list_display = [
        "name",
        "key_display",
        "user",
        "is_active",
        "last_used",
        "date_created",
    ]
    list_filter = ["is_active", "date_created", "last_used"]
    search_fields = ["name", "user__email", "user__name", "key_prefix"]
    readonly_fields = [
        "key_prefix",
        "key_hash",
        "last_used",
        "date_created",
        "date_updated",
    ]
    fields = [
        "user",
        "name",
        "key_prefix",
        "key_hash",
        "is_active",
        "last_used",
        "date_created",
        "date_updated",
    ]
    
    def key_display(self, obj):
        """Display truncated key prefix."""
        if obj.key_prefix:
            return format_html('<code>{}</code>', obj.key_prefix + "...")
        return "-"
    key_display.short_description = "Key"
    
    def save_model(self, request, obj, form, change):
        """Handle API key creation - generate key on first save."""
        if not change and not obj.key_hash:  # Creating new key
            # Generate the key
            key = ApiKey.generate_key()
            obj.set_key(key)
            # Save the object
            super().save_model(request, obj, form, change)
            # Show the key to the admin (only time it's visible)
            messages.add_message(
                request,
                messages.SUCCESS,
                format_html(
                    '<strong>API Key created!</strong><br>'
                    '<code style="background: #f0f0f0; padding: 4px 8px; border-radius: 4px; display: inline-block; margin: 8px 0;">{}</code><br>'
                    '<small>⚠️ Save this key now - it will not be shown again.</small>',
                    key
                ),
            )
        else:
            super().save_model(request, obj, form, change)

