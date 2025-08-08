from typing import Optional, Dict

from api.models import SenioritySnapshot, User, LadderAspect
from api.models.ladder import LadderStage
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
        "max_level": 7,
        "user_stage": "MID"
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
    max_level = 0
    user_stage = None
    
    if snapshot.ladder and snapshot.details_json:
        # Get max_level for this ladder
        max_level = snapshot.ladder.get_max_level()
        
        # Get aspect names for this ladder
        aspect_names = {}
        for aspect in LadderAspect.objects.filter(ladder=snapshot.ladder):
            aspect_names[aspect.code] = aspect.name
        
        # Map codes to names in details
        for code, level in snapshot.details_json.items():
            aspect_name = aspect_names.get(code, code)  # Fallback to code if name not found
            details_with_names[aspect_name] = level
            
        # Get user's overall stage from stages_json
        if snapshot.stages_json:
            stage_counts = {}
            for stage in snapshot.stages_json.values():
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Get the most common stage
            if stage_counts:
                # If there's a tie, prefer the stage that appears later in LadderStage choices
                # This gives priority to higher stages (LATE > MID > EARLY)
                stage_choices = [choice[0] for choice in LadderStage.choices]
                user_stage = max(stage_counts.keys(), key=lambda x: (stage_counts[x], stage_choices.index(x)))
    else:
        # If no ladder or details, return as is
        details_with_names = snapshot.details_json
    
    return {
        "overall": snapshot.overall_score,
        "details": details_with_names,
        "max_level": max_level,
        "user_stage": user_stage,
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