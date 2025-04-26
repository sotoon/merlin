class CycleQueryParamMixin:
    def get_cycle(self):
        cycle = self.request.query_params.get('cycle', None)
        return cycle

    def filter_queryset(self, queryset):
        cycle = self.get_cycle()
        if cycle is not None:
            queryset = queryset.filter(cycle__uuid=cycle)
        return super().filter_queryset(queryset)
