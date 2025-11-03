"""Utilities for working with seniority levels."""

from typing import Optional
from api.models import User, SenioritySnapshot

__all__ = ["get_latest_seniority_level", "populate_seniority_level_for_user"]


def get_latest_seniority_level(user: User, as_of_date=None) -> Optional[str]:
    """Get the latest seniority level for a user from their seniority snapshots.
    
    Args:
        user: User instance
        as_of_date: Optional date to get seniority level as-of that date
        
    Returns:
        Seniority level string (JUNIOR, MID, SENIOR, PRINCIPAL) or None
    """
    from datetime import date
    
    qs = SenioritySnapshot.objects.filter(
        user=user,
        seniority_level__isnull=False
    )
    
    if as_of_date:
        qs = qs.filter(effective_date__lte=as_of_date)
    
    latest = qs.order_by('-effective_date', '-date_created').first()
    return latest.seniority_level if latest else None


def populate_seniority_level_for_user(user: User, seniority_level: str, effective_date=None):
    """Update the latest seniority snapshot for a user with seniority_level.
    
    If no seniority snapshot exists, uses the latest one or creates a placeholder.
    Updates the seniority_level on the most recent snapshot.
    
    Args:
        user: User instance
        seniority_level: One of JUNIOR, MID, SENIOR, PRINCIPAL
        effective_date: Date for the snapshot (defaults to today)
    """
    from datetime import date
    from api.models import Ladder
    
    if effective_date is None:
        effective_date = date.today()
    
    # Validate seniority_level
    valid_levels = [choice[0] for choice in SenioritySnapshot.SeniorityLevel.choices]
    if seniority_level not in valid_levels:
        raise ValueError(f"Invalid seniority_level. Must be one of: {valid_levels}")
    
    # Get the latest seniority snapshot (or create a minimal one if none exists)
    latest_snapshot = SenioritySnapshot.objects.filter(
        user=user
    ).order_by('-effective_date', '-date_created').first()
    
    if latest_snapshot:
        # Update the latest snapshot's seniority_level
        latest_snapshot.seniority_level = seniority_level
        latest_snapshot.save(update_fields=['seniority_level'])
    else:
        # Create a minimal snapshot if none exists
        # Try to get a ladder from the user's latest snapshot or use a default
        default_ladder = Ladder.objects.first()
        SenioritySnapshot.objects.create(
            user=user,
            ladder=default_ladder,
            title="",
            overall_score=0.0,
            details_json={},
            stages_json={},
            seniority_level=seniority_level,
            effective_date=effective_date,
        )

