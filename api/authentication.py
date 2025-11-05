"""Custom authentication classes for DRF."""

from rest_framework import authentication, exceptions
from django.utils import timezone

from api.models import ApiKey

__all__ = ["ApiKeyAuthentication"]


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Authentication using API keys in the X-API-Key header.
    
    Usage:
        1. Client sends request with header: X-API-Key: pk_live_...
        2. We look up the key by prefix (first 12 chars) for efficiency
        3. Verify the full key matches
        4. Return the associated user and ApiKey instance
    """
    header_name = 'X-API-Key'

    def authenticate(self, request):
        """Authenticate the request using API key from header."""
        api_key = request.META.get(self.header_name, None)
        
        if not api_key:
            return None  # Let other authentication classes try
        
        # Validate key format (starts with pk_live_)
        if not api_key.startswith('pk_live_'):
            raise exceptions.AuthenticationFailed('Invalid API key format.')
        
        # Extract prefix for lookup
        key_prefix = api_key[:12]
        
        # Find active API keys with matching prefix
        try:
            api_key_obj = ApiKey.objects.filter(
                key_prefix=key_prefix,
                is_active=True
            ).select_related('user').first()
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')
        
        if not api_key_obj:
            raise exceptions.AuthenticationFailed('Invalid API key.')
        
        # Verify the key matches
        if not api_key_obj.verify_key(api_key):
            raise exceptions.AuthenticationFailed('Invalid API key.')
        
        # Record usage
        api_key_obj.record_usage()
        
        # Return (user, auth) tuple
        # The auth object can be the ApiKey instance for later access if needed
        return (api_key_obj.user, api_key_obj)

