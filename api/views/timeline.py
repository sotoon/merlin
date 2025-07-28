from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import mixins, viewsets

from api.models import User, TimelineEvent, RoleType, TitleChange, Notice
from api.serializers.timeline import (
    TimelineEventLiteSerializer,
    TitleChangeSerializer,
    NoticeSerializer,
    # StockGrantSerializer,  # Disabled until endpoint is finalised
)
from api.services import can_view_timeline, has_role
from api.utils import get_current_level


__all__ = ["UserTimelineView", "TitleChangeViewSet", "NoticeViewSet"]


class IsMaintainer(IsAuthenticated):
    """Allow only users with the Maintainer role type or staff."""

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            from api.services import has_role
            return request.user.is_staff or has_role(request.user, {RoleType.MAINTAINER})
        return False


class UserTimelineView(ListAPIView):
    """Return paginated timeline events for a given user_id respecting feature flag and basic ACL."""

    serializer_class = TimelineEventLiteSerializer
    permission_classes = [IsAuthenticated]

    class _Pagination(PageNumberPagination):
        page_size = 10

    pagination_class = _Pagination

    def get_queryset(self):
        target_user = get_object_or_404(User, uuid=self.kwargs["user_id"])
        request_user = self.request.user

        # Feature flag – allow only when enabled
        flag = getattr(settings, "FEATURE_CAREER_TIMELINE_ACCESS", "off")
        if flag == "off":
            raise PermissionDenied("Profile timeline feature is disabled.")
        if flag == "dev" and not request_user.is_staff:
            raise PermissionDenied("Profile timeline feature restricted to devs.")
        if flag == "hr":
            # Basic check: require HR role – fallback to is_staff if role system not implemented

            if (not has_role(request_user, {RoleType.HR_MANAGER})
                    and not request_user.is_staff):
                raise PermissionDenied("Profile timeline restricted to HR.")

        # Fine-grained ACL check
        if not can_view_timeline(request_user, target_user) and not request_user.is_staff:
            raise PermissionDenied("You do not have permission to view this timeline.")

        return (
            TimelineEvent.objects.filter(user=target_user)
            .order_by("-effective_date", "-date_created")
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if request.query_params.get("include_level") == "true":
            target_user = get_object_or_404(User, uuid=self.kwargs["user_id"])
            level_data = get_current_level(target_user)
            if level_data:
                response.data["level"] = level_data
        return response


# Write endpoint for title changes (Maintainer only)
class TitleChangeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TitleChange.objects.select_related("user")
    serializer_class = TitleChangeSerializer
    permission_classes = [IsMaintainer]
    pagination_class = None 


# Read-only endpoints for Notice & StockGrant
class NoticeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Notice.objects.select_related("user")
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


# class StockGrantViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
#     """Disabled until stock-grant detail endpoint is finalised."""
#     queryset = StockGrant.objects.select_related("user")
#     serializer_class = StockGrantSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = None 