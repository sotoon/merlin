from typing import Optional, Dict

from api.models import SenioritySnapshot, User
from api.models.timeline import TitleChange

__all__ = [
    "get_current_level",
    "get_current_job_title",
]


def get_current_level(user: User) -> Optional[Dict]:
    """Return the latest seniority data for the user or None.

    Example output:
    {
        "overall": 2.4,
        "details": {"Design": 3, ...}
    }
    """
    snapshot = (
        SenioritySnapshot.objects.filter(user=user)
        .order_by("-effective_date", "-date_created")
        .values("overall_score", "details_json")
        .first()
    )
    if not snapshot:
        return None
    return {
        "overall": snapshot["overall_score"],
        "details": snapshot["details_json"],
    }


def get_current_job_title(user: User) -> Optional[str]:
    """Return the current job title from the latest TitleChange record or None."""
    title_change = (
        TitleChange.objects.filter(user=user)
        .order_by("-effective_date", "-date_created")
        .values("new_title")
        .first()
    )
    if not title_change:
        return None
    return title_change["new_title"] or None 