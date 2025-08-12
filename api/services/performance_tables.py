from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable, Optional

from django.db.models import OuterRef, Subquery, Max, Q, Exists, Count

from api.models import (
    User,
    TimelineEvent,
    CompensationSnapshot,
    SenioritySnapshot,
    OrgAssignmentSnapshot,
    Note,
    Summary,
    DataAccessOverride,
)
from api.services.timeline_access import can_view_timeline, has_role, TECH_LADDERS, PRODUCT_LADDERS
from api.models import RoleType
from api.utils.performance_tables import get_persian_year_bounds_gregorian

__all__ = [
    "get_visible_users_for_viewer",
    "build_personnel_performance_queryset",
    "apply_personnel_filters",
    "apply_personnel_ordering",
]


def get_visible_users_for_viewer(viewer: User, as_of: Optional[date] = None) -> Iterable[User]:
    """Return a queryset of users visible to the viewer using coarse DB-side constraints
    derived from role scopes, with a final safety pass via can_view_timeline.

    Directors are additionally filtered by ladder category using the latest SenioritySnapshot as-of.
    CTO/VP see all technical users; CPO sees all product managers (by ladder), org-wide.
    """
    qs = User.objects.select_related("team", "team__tribe", "chapter", "department")
    as_of = as_of or date.today()

    # DataAccessOverride: honor explicit overrides first
    now = datetime.now(timezone.utc)
    override = DataAccessOverride.objects.filter(user=viewer, is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).order_by("-date_created").first()
    if override:
        latest_sen_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"), effective_date__lte=as_of)
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        if override.scope == DataAccessOverride.Scope.ALL:
            return qs
        if override.scope == DataAccessOverride.Scope.TECH:
            return qs.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=TECH_LADDERS)
        if override.scope == DataAccessOverride.Scope.PRODUCT:
            return qs.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=PRODUCT_LADDERS)

    # Prepare latest seniority ladder code as-of (used in many branches)
    latest_sen_ladder_code = Subquery(
        SenioritySnapshot.objects
        .filter(user=OuterRef("pk"), effective_date__lte=as_of)
        .order_by("-effective_date", "-date_created")
        .values("ladder__code")[:1]
    )

    # HR/CEO/Maintainer: unrestricted
    if has_role(viewer, {RoleType.HR_MANAGER, RoleType.CEO, RoleType.MAINTAINER}):
        return qs

    # CTO/VP: all technical users
    if has_role(viewer, {RoleType.CTO, RoleType.VP}):
        return qs.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=TECH_LADDERS)

    # CPO: all product managers
    if has_role(viewer, {RoleType.CPO}):
        return qs.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=PRODUCT_LADDERS)

    # Directors/Principals (treat principals as directors): tribe-scoped + ladder category
    if has_role(viewer, {RoleType.PRODUCT_DIRECTOR, RoleType.ENGINEERING_DIRECTOR}):
        viewer_tribe_id = getattr(getattr(viewer.team, "tribe", None), "pk", None)
        if not viewer_tribe_id:
            return qs.none()

        tribe_scoped = qs.filter(team__tribe_id=viewer_tribe_id)

        if has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
            return tribe_scoped.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=TECH_LADDERS)

        # Product director
        return tribe_scoped.annotate(_ladder_code=latest_sen_ladder_code).filter(_ladder_code__in=PRODUCT_LADDERS)

    # Team leaders: team-scoped
    if qs.filter(team__leader=viewer).exists():
        return qs.filter(team__leader=viewer)

    # Fallback: start with all; final filtering via can_view_timeline in the view
    return qs


def build_personnel_performance_queryset(viewer: User, as_of: Optional[date]):
    """Build a queryset annotated with latest as-of metrics for the personnel performance table."""
    as_of = as_of or date.today()

    # Compute Persian year bounds for current and last years based on as_of
    cur_start, cur_end = get_persian_year_bounds_gregorian(as_of)
    # last Persian year bounds: subtract 1 jalali year by shifting ref_date one day before cur_start
    last_ref = cur_start.replace(day=max(1, cur_start.day))
    from datetime import timedelta
    last_ref = cur_start - timedelta(days=1)
    last_start, last_end = get_persian_year_bounds_gregorian(last_ref)

    # Latest compensation snapshot as-of
    latest_comp_qs = (
        CompensationSnapshot.objects
        .filter(user=OuterRef("pk"), effective_date__lte=as_of)
        .order_by("-effective_date", "-date_created")
    )
    latest_comp_ids = Subquery(latest_comp_qs.values("pk")[:1])

    # Latest seniority snapshot as-of
    latest_sen_qs = (
        SenioritySnapshot.objects
        .filter(user=OuterRef("pk"), effective_date__lte=as_of)
        .order_by("-effective_date", "-date_created")
    )
    latest_sen_ids = Subquery(latest_sen_qs.values("pk")[:1])

    # Latest org assignment as-of
    latest_org_qs = (
        OrgAssignmentSnapshot.objects
        .filter(user=OuterRef("pk"), effective_date__lte=as_of)
        .order_by("-effective_date", "-date_created")
    )
    latest_org_ids = Subquery(latest_org_qs.values("pk")[:1])

    # Last committee date: from Summary of specific proposal types
    last_committee_date = Subquery(
        Summary.objects.filter(
            note__owner=OuterRef("pk"),
            committee_date__lte=as_of,
            note__proposal_type__in=["PROMOTION", "EVALUATION", "MAPPING"],
        )
        .order_by("-committee_date")
        .values("committee_date")[:1]
    )

    # Counts of committees in current and last Persian years
    committee_types = ["PROMOTION", "EVALUATION", "MAPPING"]
    committees_current_year = Subquery(
        Summary.objects.filter(
            note__owner=OuterRef("pk"),
            committee_date__gte=cur_start,
            committee_date__lte=cur_end,
            note__proposal_type__in=committee_types,
        )
        .order_by()  # required to use values/count in subquery on some DBs
        .values("note__owner")
        .annotate(c=Count("id"))
        .values("c")[:1]
    )
    committees_last_year = Subquery(
        Summary.objects.filter(
            note__owner=OuterRef("pk"),
            committee_date__gte=last_start,
            committee_date__lte=last_end,
            note__proposal_type__in=committee_types,
        )
        .order_by()
        .values("note__owner")
        .annotate(c=Count("id"))
        .values("c")[:1]
    )

    # Last bonus snapshot as-of (date and percentage)
    last_bonus_date = Subquery(
        CompensationSnapshot.objects.filter(
            user=OuterRef("pk"), effective_date__lte=as_of, bonus_percentage__gt=0
        ).order_by("-effective_date", "-date_created").values("effective_date")[:1]
    )
    last_bonus_percentage = Subquery(
        CompensationSnapshot.objects.filter(
            user=OuterRef("pk"), effective_date__lte=as_of, bonus_percentage__gt=0
        ).order_by("-effective_date", "-date_created").values("bonus_percentage")[:1]
    )

    # As-of fields
    pay_band_number = Subquery(latest_comp_qs.values("pay_band__number")[:1])
    salary_change = Subquery(latest_comp_qs.values("salary_change")[:1])

    ladder_code = Subquery(latest_sen_qs.values("ladder__code")[:1])
    overall_score = Subquery(latest_sen_qs.values("overall_score")[:1])
    details_json = Subquery(latest_sen_qs.values("details_json")[:1])

    leader_name = Subquery(latest_org_qs.values("leader__name")[:1])
    team_name = Subquery(latest_org_qs.values("team__name")[:1])
    tribe_name = Subquery(latest_org_qs.values("team__tribe__name")[:1])

    is_mapped = Exists(SenioritySnapshot.objects.filter(user=OuterRef("pk")))

    qs = (
        get_visible_users_for_viewer(viewer, as_of)
        .annotate(_latest_comp_id=latest_comp_ids)
        .annotate(_latest_sen_id=latest_sen_ids)
        .annotate(_latest_org_id=latest_org_ids)
        .annotate(_last_committee_date=last_committee_date)
        .annotate(_committees_current_year=committees_current_year, _committees_last_year=committees_last_year)
        .annotate(_last_bonus_date=last_bonus_date, _last_bonus_percentage=last_bonus_percentage)
        .annotate(
            _pay_band_number=pay_band_number,
            _salary_change=salary_change,
            _ladder_code=ladder_code,
            _overall_score=overall_score,
            _details_json=details_json,
            _leader_name=leader_name,
            _team_name=team_name,
            _tribe_name=tribe_name,
            _is_mapped=is_mapped,
        )
        .select_related("team", "leader", "team__tribe")
    )

    return qs


def apply_personnel_filters(qs, params: dict):
    """Apply common filters on the annotated queryset using query params."""
    team_id = params.get("team")
    tribe_id = params.get("tribe")
    leader_id = params.get("leader")
    ladder = params.get("ladder")
    pay_band_min = params.get("pay_band_min")
    pay_band_max = params.get("pay_band_max")
    mapped = params.get("mapped")
    evaluated_after = params.get("evaluated_after")  # YYYY-MM-DD
    evaluated_before = params.get("evaluated_before")

    if team_id:
        qs = qs.filter(_team_name__isnull=False, team_id=team_id)
    if tribe_id:
        qs = qs.filter(team__tribe_id=tribe_id)
    if leader_id:
        qs = qs.filter(leader_id=leader_id)
    if ladder:
        qs = qs.filter(_ladder_code=ladder)
    if pay_band_min:
        qs = qs.filter(_pay_band_number__gte=pay_band_min)
    if pay_band_max:
        qs = qs.filter(_pay_band_number__lte=pay_band_max)
    if mapped is not None:
        if mapped in ("1", "true", "True", True):
            qs = qs.filter(_is_mapped=True)
        elif mapped in ("0", "false", "False", False):
            qs = qs.filter(_is_mapped=False)
    if evaluated_after:
        qs = qs.filter(_last_committee_date__gte=evaluated_after)
    if evaluated_before:
        qs = qs.filter(_last_committee_date__lte=evaluated_before)

    return qs


def apply_personnel_ordering(qs, ordering_param: Optional[str]):
    """Order the annotated queryset by supported fields.
    Supports comma-separated fields with optional '-' prefix for descending.
    """
    if not ordering_param:
        return qs

    ordering_map = {
        "name": "name",
        "pay_band": "_pay_band_number",
        "last_committee_date": "_last_committee_date",
        "committees_current_year": "_committees_current_year",
        "committees_last_year": "_committees_last_year",
        "overall_level": "_overall_score",
        "team": "_team_name",
        "leader": "_leader_name",
        "tribe": "_tribe_name",
        "ladder": "_ladder_code",
    }

    order_by_clauses = []
    for token in ordering_param.split(","):
        token = token.strip()
        if not token:
            continue
        desc = token.startswith("-")
        key = token[1:] if desc else token
        field = ordering_map.get(key)
        if not field:
            continue
        order_by_clauses.append(("-" if desc else "") + field)

    if not order_by_clauses:
        return qs

    return qs.order_by(*order_by_clauses) 