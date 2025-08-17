from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import User, Team, Tribe
from api.serializers.user_access import (
    UserPermissionsSerializer,
    AccessibleUsersResponseSerializer,
    TimelinePermissionsSerializer,
)
from api.services.timeline_access import (
    can_view_timeline, 
    has_role, 
    TECH_LADDERS, 
    PRODUCT_LADDERS,
    _is_technical,
    _is_product
)
from api.models import RoleType, SenioritySnapshot
from django.db.models import Q, Subquery, OuterRef, Exists


@extend_schema(responses={200: UserPermissionsSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """Get current user's permissions and accessible data for UI configuration."""
    user = request.user
    
    # Determine user's roles
    roles = []
    if has_role(user, {RoleType.CEO}):
        roles.append("CEO")
    if has_role(user, {RoleType.CTO}):
        roles.append("CTO")
    if has_role(user, {RoleType.VP}):
        roles.append("VP")
    if has_role(user, {RoleType.CPO}):
        roles.append("CPO")
    if has_role(user, {RoleType.CFO}):
        roles.append("CFO")
    if has_role(user, {RoleType.HR_MANAGER}):
        roles.append("HR_MANAGER")
    if has_role(user, {RoleType.ENGINEERING_DIRECTOR}):
        roles.append("ENGINEERING_DIRECTOR")
    if has_role(user, {RoleType.PRODUCT_DIRECTOR}):
        roles.append("PRODUCT_DIRECTOR")
    if has_role(user, {RoleType.MAINTAINER}):
        roles.append("MAINTAINER")
    if has_role(user, {RoleType.SALES_MANAGER}):
        roles.append("SALES_MANAGER")
    
    # Check if user is a team leader
    if Team.objects.filter(leader=user).exists():
        roles.append("TEAM_LEADER")
    
    # Determine permissions
    can_view_all_users = has_role(user, {RoleType.CEO, RoleType.HR_MANAGER, RoleType.MAINTAINER})
    can_view_technical_users = has_role(user, {RoleType.CTO, RoleType.VP}) or has_role(user, {RoleType.ENGINEERING_DIRECTOR})
    can_view_product_users = has_role(user, {RoleType.CPO}) or has_role(user, {RoleType.PRODUCT_DIRECTOR})

    # Visibility of performance table (Team Leaders and above + Agile Coaches)
    is_team_leader = Team.objects.filter(leader=user).exists()
    is_agile_coach = User.objects.filter(agile_coach=user).exists()
    can_view_performance_table = (
        is_team_leader
        or has_role(user, {RoleType.ENGINEERING_DIRECTOR, RoleType.PRODUCT_DIRECTOR, RoleType.CTO, RoleType.CFO, RoleType.CEO, RoleType.HR_MANAGER, RoleType.SALES_MANAGER, RoleType.VP, RoleType.MAINTAINER})
        or is_agile_coach
    )
    
    # Determine accessible ladders (names)
    accessible_ladders = []
    from api.models import Ladder
    if can_view_all_users:
        accessible_ladders = list(Ladder.objects.values_list("name", flat=True))
    elif has_role(user, {RoleType.CTO, RoleType.VP}):
        accessible_ladders = list(Ladder.objects.filter(code__in=TECH_LADDERS).values_list("name", flat=True))
    elif has_role(user, {RoleType.ENGINEERING_DIRECTOR}):
        tribe = getattr(getattr(user.team, "tribe", None), "pk", None)
        if tribe:
            names = (
                SenioritySnapshot.objects
                .filter(user__team__tribe_id=tribe, ladder__code__in=TECH_LADDERS)
                .values_list("ladder__name", flat=True)
                .distinct()
            )
            accessible_ladders = list(names)
    elif has_role(user, {RoleType.PRODUCT_DIRECTOR}) or has_role(user, {RoleType.CPO}):
        accessible_ladders = list(Ladder.objects.filter(code__in=PRODUCT_LADDERS).values_list("name", flat=True))
    elif has_role(user, {RoleType.CFO}):
        # Finance + general non-tech if present
        candidates = ["Finance Ladder", "General Ladder"]
        accessible_ladders = list(Ladder.objects.filter(name__in=candidates).values_list("name", flat=True))
    elif has_role(user, {RoleType.SALES_MANAGER}):
        candidates = ["Sales Ladder", "General Ladder"]
        accessible_ladders = list(Ladder.objects.filter(name__in=candidates).values_list("name", flat=True))

    # Determine accessible tribes
    accessible_tribes = []
    if can_view_all_users:
        # HR and CEO can see all tribes
        accessible_tribes = list(Tribe.objects.values_list('name', flat=True))
    elif has_role(user, {RoleType.ENGINEERING_DIRECTOR}):
        # Engineering directors can see their own tribe
        if user.team and user.team.tribe:
            accessible_tribes = [user.team.tribe.name]
    elif has_role(user, {RoleType.PRODUCT_DIRECTOR}):
        # Product directors can see their own tribe
        if user.team and user.team.tribe:
            accessible_tribes = [user.team.tribe.name]
    elif has_role(user, {RoleType.CTO, RoleType.VP}):
        # CTO/VP: tribes with (any TECH user by latest ladder) OR (unmapped users in TECH tribe/team)
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        tech_tribe_ids_from_ladder = User.objects.annotate(_ladder_code=latest_ladder_code).filter(
            _ladder_code__in=TECH_LADDERS
        ).values("team__tribe_id")
        unmapped_tech_tribe_ids = User.objects.filter(
            seniority_snapshots__isnull=True
        ).filter(
            Q(team__tribe__category="TECH") | Q(team__category="TECH")
        ).values("team__tribe_id")
        accessible_tribes = list(
            Tribe.objects.filter(
                Q(pk__in=Subquery(tech_tribe_ids_from_ladder)) | Q(pk__in=Subquery(unmapped_tech_tribe_ids))
            ).values_list('name', flat=True).distinct()
        )
    elif has_role(user, {RoleType.CPO}):
        # CPO: tribes with at least one user whose latest ladder is PRODUCT OR belongs to Product chapter
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        product_tribe_ids_from_ladder = User.objects.annotate(_ladder_code=latest_ladder_code).filter(
            _ladder_code__in=PRODUCT_LADDERS
        ).values("team__tribe_id")
        product_tribe_ids_from_chapter = User.objects.filter(chapter__name__iexact="Product").values("team__tribe_id")
        accessible_tribes = list(
            Tribe.objects.filter(
                Q(pk__in=Subquery(product_tribe_ids_from_ladder)) | Q(pk__in=Subquery(product_tribe_ids_from_chapter))
            ).values_list('name', flat=True).distinct()
        )
    elif has_role(user, {RoleType.CFO}):
        # CFO: finance tribe only
        accessible_tribes = list(Tribe.objects.filter(name="Finance").values_list('name', flat=True))
    elif has_role(user, {RoleType.SALES_MANAGER}):
        # Sales manager: tribes under Sales department
        accessible_tribes = list(Tribe.objects.filter(department__name="Sales").values_list('name', flat=True))
    
    # Determine accessible teams
    accessible_teams = []
    if can_view_all_users:
        # HR, CEO, Maintainer can see all teams
        accessible_teams = list(Team.objects.values_list('name', flat=True))
    elif Team.objects.filter(leader=user).exists():
        # Team leaders can see their own team
        accessible_teams = list(Team.objects.filter(leader=user).values_list('name', flat=True))
    elif accessible_tribes:
        # Directors can see teams in their accessible tribes
        accessible_teams = list(Team.objects.filter(tribe__name__in=accessible_tribes).values_list('name', flat=True))
    elif has_role(user, {RoleType.CTO, RoleType.VP}):
        # CTO/VP: teams with (any TECH user by latest ladder) OR (unmapped users AND team/tribe categorized as TECH)
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        tech_team_ids = User.objects.annotate(_ladder_code=latest_ladder_code).filter(
            _ladder_code__in=TECH_LADDERS
        ).values("team_id")
        accessible_teams = list(
            Team.objects.filter(
                Q(pk__in=Subquery(tech_team_ids))
                | (
                    Q(user__seniority_snapshots__isnull=True)
                    & (Q(category="TECH") | Q(tribe__category="TECH"))
                )
            ).values_list('name', flat=True).distinct()
        )
    elif has_role(user, {RoleType.CPO}):
        # CPO: teams with at least one user whose latest ladder is PRODUCT OR belongs to Product chapter
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        product_team_ids_from_ladder = User.objects.annotate(_ladder_code=latest_ladder_code).filter(
            _ladder_code__in=PRODUCT_LADDERS
        ).values("team_id")
        product_team_ids_from_chapter = User.objects.filter(chapter__name__iexact="Product").values("team_id")
        accessible_teams = list(
            Team.objects.filter(
                Q(pk__in=Subquery(product_team_ids_from_ladder)) | Q(pk__in=Subquery(product_team_ids_from_chapter))
            ).values_list('name', flat=True).distinct()
        )
    elif has_role(user, {RoleType.CFO}):
        # CFO: finance tribe teams only
        accessible_teams = list(Team.objects.filter(tribe__name__in=["Finance"]).values_list('name', flat=True))
    elif has_role(user, {RoleType.SALES_MANAGER}):
        # Sales manager: teams under Sales department
        accessible_teams = list(Team.objects.filter(department__name="Sales").values_list('name', flat=True))
    
    # Determine accessible leaders via 'has subordinates' (consistent with MyTeamViewSet)
    accessible_leaders = []
    leaders_qs = User.objects.none()

    if can_view_all_users:
        leaders_qs = User.objects.filter(user__isnull=False).distinct()
    elif has_role(user, {RoleType.CTO, RoleType.VP}):
        # Leaders with (any TECH subordinate by LATEST ladder) OR (unmapped subordinate AND subordinate categorized TECH)
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        tech_sub_exists = Exists(
            User.objects
            .filter(leader=OuterRef("pk"))
            .annotate(_ladder_code=latest_ladder_code)
            .filter(_ladder_code__in=TECH_LADDERS)
        )
        unmapped_tech_sub_exists = Exists(
            User.objects
            .filter(leader=OuterRef("pk"), seniority_snapshots__isnull=True)
            .filter(Q(team__category="TECH") | Q(team__tribe__category="TECH"))
        )
        leaders_qs = User.objects.filter(tech_sub_exists | unmapped_tech_sub_exists).distinct()
    elif has_role(user, {RoleType.CPO}):
        # Leaders with (any PRODUCT subordinate by LATEST ladder) OR (subordinate in Product chapter)
        latest_ladder_code = Subquery(
            SenioritySnapshot.objects
            .filter(user=OuterRef("pk"))
            .order_by("-effective_date", "-date_created")
            .values("ladder__code")[:1]
        )
        product_sub_exists = Exists(
            User.objects
            .filter(leader=OuterRef("pk"))
            .annotate(_ladder_code=latest_ladder_code)
            .filter(_ladder_code__in=PRODUCT_LADDERS)
        )
        product_chapter_sub_exists = Exists(
            User.objects.filter(leader=OuterRef("pk"), chapter__name__iexact="Product")
        )
        leaders_qs = User.objects.filter(product_sub_exists | product_chapter_sub_exists).distinct()
    elif has_role(user, {RoleType.CFO}):
        leaders_qs = User.objects.filter(user__team__tribe__name="Finance").distinct()
    elif has_role(user, {RoleType.SALES_MANAGER}):
        leaders_qs = User.objects.filter(user__department__name="Sales").distinct()
    elif accessible_tribes:
        leaders_qs = User.objects.filter(user__team__tribe__name__in=accessible_tribes).distinct()
    elif Team.objects.filter(leader=user).exists():
        leaders_qs = User.objects.filter(pk=user.pk)

    accessible_leaders = list({(l.name or l.email) for l in leaders_qs if (l.name or l.email)})
    
    # Determine scope
    if can_view_all_users:
        scope = "all_users"
    elif can_view_technical_users:
        scope = "technical_only"
    elif can_view_product_users:
        scope = "product_only"
    elif Team.objects.filter(leader=user).exists():
        scope = "team_only"
    else:
        scope = "none"
    
    # UI hints
    ui_hints = {
        "show_timeline_section": True,  # All authenticated users can see timeline section
        "show_performance_table": can_view_performance_table,
        "filter_options": {
            "ladders": accessible_ladders,
            "tribes": accessible_tribes,
            "teams": accessible_teams,
            "leaders": accessible_leaders,
        }
    }
    
    return Response({
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "roles": roles,
            "organization": getattr(user.organization, 'name', None),
        },
        "permissions": {
            "can_view_all_users": can_view_all_users,
            "can_view_technical_users": can_view_technical_users,
            "can_view_product_users": can_view_product_users,
            "accessible_ladders": accessible_ladders,
            "accessible_tribes": accessible_tribes,
            "accessible_teams": accessible_teams,
            "accessible_leaders": accessible_leaders,
            "scope": scope,
        },
        "ui_hints": ui_hints,
    })


@extend_schema(responses={200: TimelinePermissionsSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def timeline_permissions(request, target_id):
    """Check if current user can view a specific user's timeline."""
    viewer = request.user
    target = get_object_or_404(User, uuid=target_id)
    
    can_view = can_view_timeline(viewer, target)
    
    # Determine reason
    reason = "denied"
    if viewer.pk == target.pk:
        reason = "self"
    elif has_role(viewer, {RoleType.HR_MANAGER}):
        reason = "hr_manager"
    elif viewer in target.get_leaders():
        reason = "leadership_chain"
    elif has_role(viewer, {RoleType.CEO}):
        reason = "ceo"
    elif has_role(viewer, {RoleType.CTO, RoleType.VP}) and _is_technical(target):
        reason = "technical_user"
    elif has_role(viewer, {RoleType.CPO}) and _is_product(target):
        reason = "product_user"
    elif has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}) and _is_technical(target):
        reason = "engineering_director_technical"
    elif has_role(viewer, {RoleType.PRODUCT_DIRECTOR}) and _is_product(target):
        reason = "product_director_product"
    
    latest_snapshot = target.seniority_snapshots.order_by("-effective_date").first()
    target_info = {
        "ladder": getattr(latest_snapshot.ladder, "code", None)
        if latest_snapshot
        else None,
        "tribe": getattr(getattr(target.team, "tribe", None), "name", None),
        "team": getattr(target.team, "name", None),
        "is_technical": _is_technical(target),
        "is_product": _is_product(target),
    }
    
    return Response({
        "can_view": can_view,
        "reason": reason,
        "target_info": target_info,
    })


@extend_schema(responses={200: AccessibleUsersResponseSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accessible_users(request):
    """Get list of users accessible to current user for performance table."""
    viewer = request.user
    
    # Get all users that the viewer can access
    accessible_users = []
    all_users = User.objects.filter(is_superuser=False).select_related('team', 'team__tribe')
    
    for user in all_users:
        if can_view_timeline(viewer, user):
            latest_snapshot = user.seniority_snapshots.order_by('-effective_date').first()
            accessible_users.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "ladder": getattr(latest_snapshot.ladder, 'code', None) if latest_snapshot else None,
                "tribe": getattr(getattr(user.team, 'tribe', None), 'name', None),
                "team": getattr(user.team, 'name', None),
            })
    
    # Determine scope
    scope = "all_users"
    if has_role(viewer, {RoleType.CTO, RoleType.VP}):
        scope = "technical_only"
    elif has_role(viewer, {RoleType.CPO}):
        scope = "product_only"
    elif has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
        scope = "engineering_director"
    elif has_role(viewer, {RoleType.PRODUCT_DIRECTOR}):
        scope = "product_director"
    elif has_role(viewer, {RoleType.MAINTAINER}):
        scope = "maintainer"
    elif has_role(viewer, {RoleType.SALES_MANAGER}):
        scope = "sales_manager"
    elif Team.objects.filter(leader=viewer).exists():
        scope = "team_only"
    
    return Response({
        "accessible_users": accessible_users,
        "total_count": len(accessible_users),
        "scope": scope,
    }) 