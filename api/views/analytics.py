from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import OneOnOne, Cycle

class PerformanceSummaryReport(APIView):
    permission_classes = [IsAuthenticated]                      # FUTURE ENHANCEMENT: extend with role checks after merging add-roles

    def get(self, request):
        cycle_id = request.query_params.get("cycle") or Cycle.get_current_cycle().id
        leader_id = request.query_params.get("leader_id")
        qs = OneOnOne.objects.filter(cycle_id=cycle_id)
        if leader_id:
            qs = qs.filter(note__owner_id=leader_id)
        data = qs.values(
            "member_id", "member__first_name", "member__last_name",
            "performance_summary", "leader_vibe", "member_vibe", "note__date",
        ).order_by("member_id", "note__date")
        return Response(data)