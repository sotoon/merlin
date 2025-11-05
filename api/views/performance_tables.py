import csv
from datetime import datetime
from io import StringIO

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from api.services.performance_tables import (
    build_personnel_performance_queryset,
    apply_personnel_filters,
    apply_personnel_ordering,
)
from api.services.timeline_access import can_view_timeline, has_role
from api.utils.performance_tables import build_csv_filename
from api.serializers.performance_tables import PerformanceTableResponseSerializer
from api.models import RoleType

__all__ = [
    "PersonnelPerformanceTableView",
    "PersonnelPerformanceCSVView",
    "is_service_account",
]


def is_service_account(user):
    """Check if user is a service account (for API integrations).
    
    Service accounts are identified by:
    1. Having MAINTAINER role
    2. Email matching configured service account patterns (from settings)
    """
    # Check for MAINTAINER role
    if has_role(user, {RoleType.MAINTAINER}):
        return True
    
    # Check email patterns (configurable via settings)
    service_account_email_patterns = getattr(settings, 'SERVICE_ACCOUNT_EMAIL_PATTERNS', [])
    if service_account_email_patterns:
        import fnmatch
        user_email = getattr(user, 'email', '') or ''
        for pattern in service_account_email_patterns:
            if fnmatch.fnmatch(user_email.lower(), pattern.lower()):
                return True
    
    return False


@extend_schema(
    responses={200: PerformanceTableResponseSerializer},
)
class PersonnelPerformanceTableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return self._json_response(request)
    

    
    def _json_response(self, request):
        """Handle JSON response"""
        as_of_str = request.query_params.get("as_of")
        as_of = None
        if as_of_str:
            try:
                as_of = datetime.strptime(as_of_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "Invalid as_of date. Use YYYY-MM-DD."}, status=400
                )

        # Build base queryset with annotations
        qs = build_personnel_performance_queryset(request.user, as_of)

        # Apply filters
        qs = apply_personnel_filters(qs, request.query_params)

        # Apply ordering
        qs = apply_personnel_ordering(qs, request.query_params.get("ordering"))

        # Filter by access per user (safety net)
        visible = []
        for u in qs:
            if can_view_timeline(request.user, u):
                visible.append(u)
        


        # Pagination
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 10))
        except ValueError:
            return Response({"detail": "Invalid page or page_size"}, status=400)
        
        # Service accounts can request larger page sizes
        max_page_size = 5000 if is_service_account(request.user) else 500
        if page_size > max_page_size:
            page_size = max_page_size
        start = (page - 1) * page_size
        end = start + page_size
        page_items = visible[start:end]

        # Serialize all requested columns
        data = []
        for u in page_items:
            row = {
                "uuid": str(u.uuid),
                "name": u.name or u.email,
                "last_committee_date": getattr(u, "_last_committee_date", None),
                "committees_current_year": getattr(u, "_committees_current_year", 0)
                or 0,
                "committees_last_year": getattr(u, "_committees_last_year", 0) or 0,
                "pay_band": getattr(u, "_pay_band_number", None),
                "salary_change": getattr(u, "_salary_change", None),
                "is_mapped": bool(getattr(u, "_is_mapped", False)),
                "last_bonus_date": getattr(u, "_last_bonus_date", None),
                "last_bonus_percentage": getattr(u, "_last_bonus_percentage", None),
                "last_salary_change_date": getattr(u, "_last_salary_change_date", None),
                "ladder": getattr(u, "_ladder_name", None),
                "ladder_levels": getattr(u, "_details_json", {}) if getattr(u, "_details_json", {}) is not None else {},
                "overall_level": getattr(u, "_overall_score", None),
                "seniority_level": getattr(u, "_seniority_level", None),
                "leader": getattr(u, "_leader_name", None)
                or getattr(u.leader, "name", None),
                "team": getattr(u, "_team_name", None) or getattr(u.team, "name", None),
                "tribe": getattr(u, "_tribe_name", None)
                or getattr(getattr(u.team, "tribe", None), "name", None),
            }
            data.append(row)



        return Response(
            {
                "count": len(visible),
                "page": page,
                "page_size": page_size,
                "results": data,
            }
        )


class PersonnelPerformanceCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle CSV export specifically"""
        as_of_str = request.query_params.get("as_of")
        as_of = None
        if as_of_str:
            try:
                as_of = datetime.strptime(as_of_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "Invalid as_of date. Use YYYY-MM-DD."}, status=400
                )

        # Build base queryset with annotations
        qs = build_personnel_performance_queryset(request.user, as_of)

        # Apply filters
        qs = apply_personnel_filters(qs, request.query_params)

        # Apply ordering
        qs = apply_personnel_ordering(qs, request.query_params.get("ordering"))

        # Filter by access per user (safety net)
        visible = []
        for u in qs:
            if can_view_timeline(request.user, u):
                visible.append(u)
        
        # Check if user has access to any data
        if not visible:
            return Response({"detail": "No data accessible to user"}, status=404)
        
        try:
            # Create full CSV with all fields
            buffer = StringIO()
            fieldnames = [
                "uuid",
                "name",
                "last_committee_date",
                "committees_current_year",
                "committees_last_year",
                "pay_band",
                "salary_change",
                "is_mapped",
                "last_bonus_date",
                "last_bonus_percentage",
                "last_salary_change_date",
                "ladder",
                "ladder_levels",
                "overall_level",
                "seniority_level",
                "leader",
                "team",
                "tribe",
            ]
            
            writer = csv.DictWriter(buffer, fieldnames=fieldnames)
            writer.writeheader()
            
            # Serialize all data for CSV
            for u in visible:
                row = {
                    "uuid": str(u.uuid),
                    "name": u.name or u.email,
                    "last_committee_date": getattr(u, "_last_committee_date", None),
                    "committees_current_year": getattr(u, "_committees_current_year", 0) or 0,
                    "committees_last_year": getattr(u, "_committees_last_year", 0) or 0,
                    "pay_band": getattr(u, "_pay_band_number", None),
                    "salary_change": getattr(u, "_salary_change", None),
                    "is_mapped": bool(getattr(u, "_is_mapped", False)),
                    "last_bonus_date": getattr(u, "_last_bonus_date", None),
                    "last_bonus_percentage": getattr(u, "_last_bonus_percentage", None),
                    "last_salary_change_date": getattr(u, "_last_salary_change_date", None),
                    "ladder": getattr(u, "_ladder_code", None),
                    "ladder_levels": getattr(u, "_details_json", {}) if getattr(u, "_details_json", {}) is not None else {},
                    "overall_level": getattr(u, "_overall_score", None),
                    "seniority_level": getattr(u, "_seniority_level", None),
                    "leader": getattr(u, "_leader_name", None) or getattr(u.leader, "name", None),
                    "team": getattr(u, "_team_name", None) or getattr(u.team, "name", None),
                    "tribe": getattr(u, "_tribe_name", None) or getattr(getattr(u.team, "tribe", None), "name", None),
                }
                writer.writerow(row)

            filename = build_csv_filename(as_of_str)
            response = StreamingHttpResponse(buffer.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = f"attachment; filename={filename}"
            return response
        except Exception as e:
            return Response({"detail": f"CSV export failed: {str(e)}"}, status=500)