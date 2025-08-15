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
        viewer_tribe = getattr(getattr(viewer.team, "tribe", None), "pk", None)
        target_tribe = getattr(getattr(target.team, "tribe", None), "pk", None)
        if viewer_tribe and viewer_tribe == target_tribe:
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
    """Heuristic: user has latest SenioritySnapshot ladder in TECH_LADDERS or chapter name matches."""
    from api.models import SenioritySnapshot

    latest_snap = (
        SenioritySnapshot.objects.filter(user=user).order_by("-effective_date", "-date_created").first()
    )
    if latest_snap and latest_snap.ladder and latest_snap.ladder.code in TECH_LADDERS:
        return True

    # fallback: chapter name
    chapter_name = getattr(user.chapter, "name", "")
    if chapter_name in TECH_LADDERS:
        return True

    return False


def _is_product(user: "User") -> bool:
    """Heuristic: user has latest SenioritySnapshot ladder in PRODUCT_LADDERS."""
    from api.models import SenioritySnapshot

    latest_snap = (
        SenioritySnapshot.objects.filter(user=user).order_by("-effective_date", "-date_created").first()
    )
    if latest_snap and latest_snap.ladder and latest_snap.ladder.code in PRODUCT_LADDERS:
        return True

    return False


def _is_finance(user: "User") -> bool:
    tribe_name = getattr(getattr(user.team, "tribe", None), "name", "")
    return tribe_name == "Finance"
