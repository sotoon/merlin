from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable, Optional

from django.db.models import OuterRef, Subquery, Max, Q, Exists, Count, F

from api.models import (
    User,
    CompensationSnapshot,
    SenioritySnapshot,
    OrgAssignmentSnapshot,
    Note,
    Summary,
    DataAccessOverride,
    Tribe,
)
from api.services.timeline_access import can_view_timeline, has_role, TECH_LADDERS, PRODUCT_LADDERS
from api.models import RoleType
from api.utils.performance_tables import get_persian_year_bounds_gregorian
from django.db.models.functions import TruncDate, Coalesce

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

    # CTO/VP: all technical users (by ladder, chapter, or org category)
    if has_role(viewer, {RoleType.CTO, RoleType.VP}):
        return (
            qs.annotate(_ladder_code=latest_sen_ladder_code)
            .filter(
                Q(_ladder_code__in=TECH_LADDERS)
                | Q(team__category="TECH")
                | Q(team__tribe__category="TECH")
                | Q(chapter__name__in=["DevOps", "Front"])
            )
        )

    # CPO: all product managers (by ladder, chapter, or org category) + direct reports
    if has_role(viewer, {RoleType.CPO}):
        return (
            qs.annotate(_ladder_code=latest_sen_ladder_code)
            .filter(
                Q(_ladder_code__in=PRODUCT_LADDERS)
                | Q(team__category="PRODUCT")
                | Q(team__tribe__category="PRODUCT")
                | Q(chapter__name__in=["Product"])
                | Q(leader=viewer)  # Include direct reports
            )
        )

    # CFO: Finance tribe only
    if has_role(viewer, {RoleType.CFO}):
        return qs.filter(team__tribe__name="Finance")

    # Sales Manager: users in Sales department
    if has_role(viewer, {RoleType.SALES_MANAGER}):
        return qs.filter(team__name="Sales")

    # Directors/Principals (treat principals as directors): tribe-scoped + ladder/category
    if has_role(viewer, {RoleType.PRODUCT_DIRECTOR, RoleType.ENGINEERING_DIRECTOR}):
        # Get viewer's tribe either from their team OR from tribes they direct
        viewer_tribe_id = getattr(getattr(viewer.team, "tribe", None), "pk", None)
        
        # If no team-based tribe, check if they're a director of any tribe
        if not viewer_tribe_id:
            if has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
                directed_tribe = Tribe.objects.filter(engineering_director=viewer).first()
                if directed_tribe:
                    viewer_tribe_id = directed_tribe.pk
            elif has_role(viewer, {RoleType.PRODUCT_DIRECTOR}):
                directed_tribe = Tribe.objects.filter(product_director=viewer).first()
                if directed_tribe:
                    viewer_tribe_id = directed_tribe.pk
        
        if not viewer_tribe_id:
            return qs.none()

        tribe_scoped = qs.filter(team__tribe_id=viewer_tribe_id).annotate(_ladder_code=latest_sen_ladder_code)

        if has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
            return tribe_scoped.filter(
                Q(_ladder_code__in=TECH_LADDERS)
                | Q(team__category="TECH")
                | Q(team__tribe__category="TECH")
                | Q(chapter__name__in=["DevOps", "Front"])
            )

        # Product director
        return tribe_scoped.filter(
            Q(_ladder_code__in=PRODUCT_LADDERS)
            | Q(team__category="PRODUCT")
            | Q(team__tribe__category="PRODUCT")
            | Q(chapter__name__in=["Product"])
        )

    # Team leaders: users who have this viewer as their direct leader
    if qs.filter(leader=viewer).exists():
        return qs.filter(leader=viewer)

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

    # Last committee date: prefer committee_date; if null, fall back to date_created
    # Include NOTICE events (which use ProposalType.EVALUATION) in committee calculations
    last_committee_date = Subquery(
        Summary.objects.filter(
            note__owner=OuterRef("pk"),
            note__proposal_type__in=["PROMOTION", "EVALUATION", "MAPPING"],
        )
        .annotate(_effective=Coalesce("committee_date", TruncDate("date_created")))
        .filter(_effective__lte=as_of)
        .order_by("-_effective")
        .values("_effective")[:1]
    )

    # Counts of committees in current and last Persian years
    # Include NOTICE events (which use ProposalType.EVALUATION) in committee calculations
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

    # Last salary change date as-of (non-zero salary_change)
    last_salary_change_date = Subquery(
        CompensationSnapshot.objects.filter(
            user=OuterRef("pk"), effective_date__lte=as_of
        ).exclude(salary_change=0)
         .order_by("-effective_date", "-date_created").values("effective_date")[:1]
    )

    # As-of fields
    pay_band_number = Subquery(latest_comp_qs.values("pay_band__number")[:1])
    salary_change = Subquery(latest_comp_qs.values("salary_change")[:1])

    ladder_code = Subquery(latest_sen_qs.values("ladder__code")[:1])
    ladder_name = Subquery(latest_sen_qs.values("ladder__name")[:1])
    overall_score = Subquery(latest_sen_qs.values("overall_score")[:1])
    details_json = Subquery(latest_sen_qs.values("details_json")[:1])

    leader_name = Subquery(latest_org_qs.values("leader__name")[:1])
    team_name = Subquery(latest_org_qs.values("team__name")[:1])
    team_id = Subquery(latest_org_qs.values("team_id")[:1])
    tribe_name = Subquery(latest_org_qs.values("team__tribe__name")[:1])
    tribe_id = Subquery(latest_org_qs.values("team__tribe_id")[:1])
    
    # Seniority level from latest seniority snapshot
    seniority_level = Subquery(latest_sen_qs.values("seniority_level")[:1])

    is_mapped = Exists(SenioritySnapshot.objects.filter(user=OuterRef("pk")))

    qs = (
        get_visible_users_for_viewer(viewer, as_of)
        .annotate(_latest_comp_id=latest_comp_ids)
        .annotate(_latest_sen_id=latest_sen_ids)
        .annotate(_latest_org_id=latest_org_ids)
        .annotate(_last_committee_date=last_committee_date)
        .annotate(_committees_current_year=committees_current_year, _committees_last_year=committees_last_year)
        .annotate(_last_bonus_date=last_bonus_date, _last_bonus_percentage=last_bonus_percentage)
        .annotate(_last_salary_change_date=last_salary_change_date)
        .annotate(
            _pay_band_number=pay_band_number,
            _salary_change=salary_change,
            _ladder_code=ladder_code,
            _ladder_name=ladder_name,
            _overall_score=overall_score,
            _details_json=details_json,
            _leader_name=leader_name,
            _team_name=team_name,
            _team_id=team_id,
            _tribe_name=tribe_name,
            _tribe_id=tribe_id,
            _seniority_level=seniority_level,
            _is_mapped=is_mapped,
        )
        .select_related("team", "leader", "team__tribe")
    )

    return qs


def apply_personnel_filters(qs, params: dict):
    """Apply common filters on the annotated queryset using query params."""
    filter_map = {
        "name": "name",
        "team": "_team_name",
        "tribe": "_tribe_name",
        "leader": "_leader_name",
        "ladder": "_ladder_name",
        "pay_band": "_pay_band_number",
        "is_mapped": "_is_mapped",
        "last_committee_date": "_last_committee_date",
        "last_bonus_date": "_last_bonus_date",
        "last_salary_change_date": "_last_salary_change_date",
        "overall_level": "_overall_score",
        "salary_change": "_salary_change",
        "committees_current_year": "_committees_current_year",
        "committees_last_year": "_committees_last_year",
        "last_bonus_percentage": "_last_bonus_percentage",
    }
    string_fields = ["name", "leader"]

    if 'name_search' in params and params['name_search']:
        qs = qs.filter(name__icontains=params['name_search'])

    for key, value in params.items():
        if not value:
            continue

        parts = key.split("__")
        field_name = parts[0]
        lookup = parts[1] if len(parts) > 1 else "exact"

        if field_name.startswith("aspect_"):
            aspect_code = field_name.split("_", 1)[1]
            if lookup in ["gt", "lt", "eq"]:
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    continue

                orm_lookup = "exact" if lookup == "eq" else lookup
                qs = qs.filter(
                    **{f"_details_json__{aspect_code}__{orm_lookup}": numeric_value}
                )
            elif lookup == "in":
                # Handle multiple aspect values (e.g., aspect_technical__in=1,2,3,4,5)
                try:
                    numeric_values = [float(v.strip()) for v in value.split(",") if v.strip()]
                    if numeric_values:
                        qs = qs.filter(**{f"_details_json__{aspect_code}__in": numeric_values})
                except (ValueError, TypeError):
                    continue
            continue

        if field_name not in filter_map:
            continue

        db_field = filter_map[field_name]

        if lookup == "in":
            if field_name == "name":
                db_field = "id"
            qs = qs.filter(**{f"{db_field}__in": value.split(",")})
        elif lookup in ["gt", "lt", "eq", "gte", "lte"]:
            try:
                if "date" in field_name:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                else:
                    value = float(value)
            except (ValueError, TypeError):
                continue

            orm_lookup = "exact" if lookup == "eq" else lookup
            qs = qs.filter(**{f"{db_field}__{orm_lookup}": value})
        elif field_name in string_fields and lookup == "exact":
            qs = qs.filter(**{f"{db_field}__icontains": value})
        elif (
            field_name in ["team", "tribe", "ladder"] and lookup == "exact"
        ):
            # Name-based filtering only (UI does not provide IDs)
            if field_name == "team":
                qs = qs.filter(_team_name__iexact=value)
            elif field_name == "tribe":
                qs = qs.filter(_tribe_name__iexact=value)
            else:  # ladder by name
                qs = qs.filter(_ladder_name__iexact=value)
        elif field_name == "is_mapped" and lookup == "exact":
            bool_value = str(value).lower() in ["true", "1"]
            qs = qs.filter(**{f"{db_field}__exact": bool_value})
        else:
            qs = qs.filter(**{f"{db_field}__{lookup}": value})

    return qs


def apply_personnel_ordering(qs, ordering_param: Optional[str]):
    """Order the annotated queryset by supported fields.
    Supports comma-separated fields with optional '-' prefix for descending.
    """
    if not ordering_param:
        return qs.order_by("name")

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
        "ladder": "_ladder_name",
        "last_bonus_percentage": "_last_bonus_percentage",
        "is_mapped": "_is_mapped",
        "last_bonus_date": "_last_bonus_date",
        "last_salary_change_date": "_last_salary_change_date",
        "salary_change": "_salary_change",
    }

    order_by_clauses = []
    for token in ordering_param.split(","):
        token = token.strip()
        if not token:
            continue
        desc = token.startswith("-")
        key = token[1:] if desc else token

        if key.startswith("aspect_"):
            aspect_code = key.split("_", 1)[1]
            field_expression = F(f"_details_json__{aspect_code}")
            if desc:
                order_by_clauses.append(field_expression.desc(nulls_last=True))
            else:
                order_by_clauses.append(field_expression.asc(nulls_last=True))
            continue

        field = ordering_map.get(key)
        if not field:
            continue

        # Handle NULL values to come last for numeric fields
        if field in [
            "_pay_band_number",
            "_last_bonus_percentage",
            "_overall_score",
            "_salary_change",
            "_committees_current_year",
            "_committees_last_year",
        ]:
            if desc:
                order_by_clauses.append(F(field).desc(nulls_last=True))
            else:
                order_by_clauses.append(F(field).asc(nulls_last=True))
        else:
            # For non-numeric fields, use regular ordering
            order_by_clauses.append(("-" if desc else "") + field)

    if not order_by_clauses:
        return qs.order_by("name")

    return qs.order_by(*order_by_clauses) 