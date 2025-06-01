from api.models import Cycle

class CycleQueryParamMixin:
    def get_cycle(self) -> bool:
        cycle = self.request.query_params.get('cycle', None)
        if cycle is not None:
            try:
                cycle = bool(cycle)
            except ValueError:
                raise ValueError("Cycle must be a true/false value.")
        return cycle

    def filter_queryset(self, queryset):
        cycle = self.get_cycle()
        if cycle is not None:
            current_cycle = Cycle.get_current_cycle()
            queryset = queryset.filter(cycle=current_cycle)
        return super().filter_queryset(queryset)
