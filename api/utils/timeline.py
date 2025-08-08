from typing import Optional, Dict

from api.models import SenioritySnapshot, User, LadderAspect
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
        "details": {"طراحی": 3, ...},
        "stages": {"طراحی": "EARLY", ...}
    }
    """
    snapshot = (
        SenioritySnapshot.objects.filter(user=user)
        .order_by("-effective_date", "-date_created")
        .select_related("ladder")
        .first()
    )
    if not snapshot:
        return None
    
    # Map aspect codes to names
    details_with_names = {}
    stages_with_names = {}
    if snapshot.ladder and snapshot.details_json:
        # Get aspect names for this ladder
        aspect_names = {}
        for aspect in LadderAspect.objects.filter(ladder=snapshot.ladder):
            aspect_names[aspect.code] = aspect.name
        
        # Map codes to names in details and stages
        for code, level in snapshot.details_json.items():
            aspect_name = aspect_names.get(code, code)  # Fallback to code if name not found
            details_with_names[aspect_name] = level
        for code, stage in (snapshot.stages_json or {}).items():
            aspect_name = aspect_names.get(code, code)
            stages_with_names[aspect_name] = stage
    else:
        # If no ladder or details, return as is
        details_with_names = snapshot.details_json
        stages_with_names = snapshot.stages_json or {}
    
    return {
        "overall": snapshot.overall_score,
        "details": details_with_names,
        "stages": stages_with_names,
        "max_level": snapshot.ladder.get_max_level() if snapshot.ladder else 0,
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