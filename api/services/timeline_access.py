from __future__ import annotations

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from api.models import User, RoleType

# Centralized ladder category codes (must match Ladder.code values)
TECH_LADDERS: Set[str] = {
    # Engineering/Technical families
    "Software",
    "Software Engineering",
    "Frontend",
    "Frontend Engineering",
    "DevOps",
    "DevOps Engineering",
    "Network",
    "Network Engineering",
    "Hardware",
    "Hardware Engineering",
    "Security",
    "Security Engineering",
    "NOC",
    "Data Center",
    "Back Office",
    # Versioned ladder codes
    "SOFT-v1",
    "FRONT-v1",
    "DEVOPS-v1",
    "NET-v1",
    "HARD-v1",
    "SEC-v1",
    "NOC-v1",
    "DC-v1",
    "BO-v1",
    "GEN-v1",
}

PRODUCT_LADDERS: Set[str] = {
    "Product",
    "Product Management",
}


__all__ = ["can_view_timeline", "has_role", "TECH_LADDERS", "PRODUCT_LADDERS"]


# -----------------------------------------------------------------------------
# Public helper
# -----------------------------------------------------------------------------

def can_view_timeline(viewer: "User", target: "User") -> bool:
    """Return True if *viewer* may read *target*'s Profile Timeline.

    The rules combine:
      • SELF (always)
      • HR roles (HR_MANAGER, HRBP) – unrestricted
      • Leadership chain – viewer is direct / indirect manager of target
      • EXEC fine-grained rules:
          – CEO  → all users
          – CTO/VP  → only users considered *technical*
          – CFO  → only users under the Finance tribe
          – CPO  → only users considered *product* (by ladder)
      • Fallback: False
    """

    # 0) Self
    if viewer.pk == target.pk:
        return True

    from api.models import RoleType  # local import

    # 1) HR roles
    if has_role(viewer, {RoleType.HR_MANAGER}):
        return True

    # Agile coach direct relationship – not modelled via RoleType
    if viewer.pk == getattr(target.agile_coach, "pk", None):
        return True

    # 2) Viewer is in target's leadership chain
    if viewer in target.get_leaders():
        return True

    # 3) Executive rules
    if has_role(viewer, {RoleType.CEO}):
        return True

    if has_role(viewer, {RoleType.CTO, RoleType.VP}):
        return _is_technical(target)

    if has_role(viewer, {RoleType.CFO}):
        return _is_finance(target)

    # Product & Engineering directors by tribe scope
    if has_role(viewer, {RoleType.PRODUCT_DIRECTOR, RoleType.ENGINEERING_DIRECTOR}):
        # Get viewer's tribe either from their team OR from tribes they direct
        viewer_tribe = getattr(getattr(viewer.team, "tribe", None), "pk", None)
        
        # If no team-based tribe, check if they're a director of any tribe
        if not viewer_tribe:
            from api.models import Tribe
            if has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
                directed_tribe = Tribe.objects.filter(engineering_director=viewer).first()
                if directed_tribe:
                    viewer_tribe = directed_tribe.pk
            elif has_role(viewer, {RoleType.PRODUCT_DIRECTOR}):
                directed_tribe = Tribe.objects.filter(product_director=viewer).first()
                if directed_tribe:
                    viewer_tribe = directed_tribe.pk
        
        target_tribe = getattr(getattr(target.team, "tribe", None), "pk", None)
        if viewer_tribe and viewer_tribe == target_tribe:
            # For engineering directors, also check if target is technical
            if has_role(viewer, {RoleType.ENGINEERING_DIRECTOR}):
                return _is_technical(target)
            # For product directors, check if target is product
            if has_role(viewer, {RoleType.PRODUCT_DIRECTOR}):
                return _is_product(target)
            return True

    # CPO to view all product managers (by ladder), org-wide
    if has_role(viewer, {RoleType.CPO}):
        return _is_product(target)

    # 4) Default deny
    return False


# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------

def has_role(user: "User", role_types: Set["RoleType"]) -> bool:
    """Return True if *user* holds **any** of the given role_types, determined by FK fields on
    Organization, Tribe, Team or Chapter models. The lookup follows the naming convention used in
    Role.clean(): role_type English label lower-cased, spaces replaced with underscores.
    """

    from api.models import Organization, Tribe, Team, Chapter  # local import

    normalized_attrs = {rt.value.lower().replace(" ", "_") for rt in role_types}

    # Return mapping of role attrs present on the model to the user.
    def _subset(model):
        fields = {f.name for f in model._meta.get_fields()}
        return {attr: user for attr in normalized_attrs if attr in fields}

    org_q = _subset(Organization)
    if org_q and Organization.objects.filter(_combine_q(org_q)).exists():
        return True

    tribe_q = _subset(Tribe)
    if tribe_q and Tribe.objects.filter(_combine_q(tribe_q)).exists():
        return True

    # Team / Chapter leader (attribute is always 'leader')
    if "leader" in normalized_attrs:
        if Team.objects.filter(leader=user).exists() or Chapter.objects.filter(leader=user).exists():
            return True

    return False


def _combine_q(attr_dict):
    """Helper: attr→user mapping to big OR Q object."""
    from django.db.models import Q  # local import to avoid global dependency if not needed

    q = Q()
    for field_name, value in attr_dict.items():
        q |= Q(**{field_name: value})
    return q


def _is_technical(user: "User") -> bool:
    """Heuristic: user has latest SenioritySnapshot ladder in TECH_LADDERS, chapter name matches, or team/tribe has TECH category.
    Excludes product managers even if they're in TECH teams by checking for product ladder."""
    from api.models import SenioritySnapshot

    latest_snap = (
        SenioritySnapshot.objects.filter(user=user).order_by("-effective_date", "-date_created").first()
    )
    
    # If user has ladder data, use that (most reliable)
    if latest_snap and latest_snap.ladder:
        if latest_snap.ladder.code in TECH_LADDERS:
            return True
        # If they have a product ladder, they're NOT technical (even if in TECH team)
        if latest_snap.ladder.code in PRODUCT_LADDERS:
            return False
    
    # Enhanced chapter-based filtering (secondary check)
    chapter_name = getattr(user.chapter, "name", "")
    if chapter_name:
        # Technical chapters
        tech_chapters = {"DevOps", "Front"}
        if any(keyword in chapter_name for keyword in tech_chapters):
            return True
        # Product chapters (explicitly exclude)
        product_chapters = {"Product"}
        if any(keyword in chapter_name for keyword in product_chapters):
            return False
    
    # Fallback: check if chapter name matches TECH_LADDERS
    if chapter_name in TECH_LADDERS:
        return True
    
    # Check team or tribe category (only if no ladder data exists)
    # This ensures product managers with ladder data are excluded
    if not latest_snap or not latest_snap.ladder:
        if user.team and user.team.category == "TECH":
            return True
        if user.tribe and user.tribe.category == "TECH":
            return True

    return False


def _is_product(user: "User") -> bool:
    """Heuristic: user has latest SenioritySnapshot ladder in PRODUCT_LADDERS, chapter name matches, or team/tribe has PRODUCT category."""
    from api.models import SenioritySnapshot

    latest_snap = (
        SenioritySnapshot.objects.filter(user=user).order_by("-effective_date", "-date_created").first()
    )
    
    # If user has ladder data, use that (most reliable)
    if latest_snap and latest_snap.ladder and latest_snap.ladder.code in PRODUCT_LADDERS:
        return True

    # Enhanced chapter-based filtering (prioritized for new employees)
    chapter_name = getattr(user.chapter, "name", "")
    if chapter_name:
        # Product chapters (explicitly include)
        product_chapters = {"Product"}
        if any(keyword in chapter_name for keyword in product_chapters):
            return True
        # Technical chapters (explicitly exclude)
        tech_chapters = {"DevOps", "Front"}
        if any(keyword in chapter_name for keyword in tech_chapters):
            return False

    # Check team or tribe category (fallback)
    if user.team and user.team.category == "PRODUCT":
        return True
    if user.tribe and user.tribe.category == "PRODUCT":
        return True

    return False


def _is_finance(user: "User") -> bool:
    tribe_name = getattr(getattr(user.team, "tribe", None), "name", "")
    return tribe_name == "Finance"
