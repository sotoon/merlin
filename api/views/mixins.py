from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.models import Cycle

class CycleQueryParamMixin:
    """
    Use ?cycle=<id> to filter by that cycle,
    or ?cycle=true|1|yes|current to filter to the current cycle.
    Omit ?cycle to see all objects.
    """
    def get_cycle(self) -> bool:
        raw = self.request.query_params.get('cycle', None)
        if raw is None:
            return None
        
        val = raw.strip().lower()

        if val in ('', '0', 'false', 'no'):
            return None
        
        if val in ('1', 'true', 'yes', 'current'):
            return Cycle.get_current_cycle()

        # If val was a cycle ID
        if val.isdigit():
            try:
                return Cycle.objects.get(pk=int(val))
            except Cycle.DoesNotExist:
                raise ValidationError({'cycle': _('Cycle with id %(id)s does not exist.') % {'id': val}})

        raise ValidationError({'cycle': _('Invalid cycle parameter. Use an integer id or true/false.')})

    def filter_queryset(self, queryset):
        cycle = self.get_cycle()
        if cycle is not None:
            queryset = queryset.filter(cycle=cycle)
        return super().filter_queryset(queryset)
