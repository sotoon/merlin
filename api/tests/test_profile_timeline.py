import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from api.models import (
    User,
    Team,
    Tribe,
    Department,
    Committee,
    Note,
    NoteType,
    Summary,
    SummarySubmitStatus,
    TitleChange,
    TimelineEvent,
    EventType,
    SenioritySnapshot,
    ProposalType,
    Cycle,
    Ladder,
    LadderAspect,
    LadderLevel,
    LadderStage
)


# ---------------------------------------------------------------------------
# Factories (minimal inline factory_boy-style helpers)
# ---------------------------------------------------------------------------


@pytest.fixture
def department(db):
    """Create a test department for test data."""
    return Department.objects.create(name="Engineering")


@pytest.fixture
def tribe(department):
    """Create a test tribe under the department."""
    return Tribe.objects.create(name="Backend", department=department)


@pytest.fixture
def team(tribe, department):
    """Create a test team under the tribe."""
    return Team.objects.create(name="API", tribe=tribe, department=department)


@pytest.fixture
def leader(db):
    """Create a test leader user."""
    return User.objects.create(email="leader@example.com", username="leader")


@pytest.fixture
def member(team, leader):
    """Create a test member user with leader and team."""
    return User.objects.create(
        email="member@example.com",
        username="member",
        leader=leader,
        team=team,
    )


@pytest.fixture
def committee(db):
    """Create a test committee for evaluation."""
    return Committee.objects.create(name="Eval-Com")


@pytest.fixture
def summary(member):
    """Create a test summary with note for timeline testing."""
    note = Note.objects.create(
        owner=member,
        title="Cycle Summary",
        content="...",
        date=timezone.now().date(),
        type=NoteType.GOAL,
    )
    return Summary.objects.create(
        note=note,
        content="Good job",
        bonus=10,
        ladder_change="L1→L2",
        salary_change=1,
        submit_status=SummarySubmitStatus.DONE,
    )


@pytest.fixture
def api_client(db):
    """Create API client for testing."""
    from rest_framework.test import APIClient   # delayed import
    return APIClient()


# ---------------------------------------------------------------------------
# Feature-flag tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_flag_off_returns_404(settings, api_client, member):
    """Timeline endpoint returns 403 when the feature flag is off."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "off"
    api_client.force_authenticate(member)
    url = reverse("api:user-timeline", args=[str(member.uuid)])
    resp = api_client.get(url)
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# ACL matrix
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_self_can_view(settings, api_client, member):
    """A user can view their own timeline when flag is 'all'."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)
    url = reverse("api:user-timeline", args=[str(member.uuid)])
    assert api_client.get(url).status_code == 200


@pytest.mark.django_db
def test_leader_can_view(settings, api_client, leader, member):
    """Direct leader can view subordinate timeline."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(leader)
    url = reverse("api:user-timeline", args=[str(member.uuid)])
    assert api_client.get(url).status_code == 200


@pytest.mark.django_db
def test_regular_user_denied(settings, api_client, member, leader):
    """Unrelated user cannot view another user's timeline."""
    stranger = User.objects.create(email="stranger@example.com", username="stranger")
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(stranger)
    url = reverse("api:user-timeline", args=[str(leader.uuid)])
    assert api_client.get(url).status_code == 403


# ---------------------------------------------------------------------------
# Signal mapping – committee types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "proposal_type, ladder, salary, bonus, expected",
    [
        (ProposalType.EVALUATION, True, True, True, [EventType.EVALUATION, EventType.SENIORITY_CHANGE, EventType.PAY_CHANGE, EventType.BONUS_PAYOUT]),
        (ProposalType.EVALUATION, True, False, False, [EventType.EVALUATION, EventType.SENIORITY_CHANGE]),
        (ProposalType.EVALUATION, False, False, False, [EventType.EVALUATION]),
        (ProposalType.PROMOTION, True, False, False, [EventType.SENIORITY_CHANGE]),
        (ProposalType.PROMOTION, False, True, False, [EventType.PAY_CHANGE]),
        (ProposalType.PROMOTION, True, True, True, [EventType.SENIORITY_CHANGE, EventType.PAY_CHANGE, EventType.BONUS_PAYOUT]),
        (ProposalType.MAPPING, True, True, False, [EventType.MAPPING, EventType.PAY_CHANGE]),
        (ProposalType.MAPPING, True, False, False, [EventType.MAPPING]),
        (ProposalType.NOTICE, False, False, False, [EventType.NOTICE]),
    ],
)
@pytest.mark.django_db
def test_summary_generates_correct_events(settings, proposal_type, ladder, salary, bonus, expected, member):
    """Summary DONE emits correct TimelineEvent(s) per committee type and data fields."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"

    committee = Committee.objects.create(name="C")
    member.committee = committee
    member.save()

    # Create ladder with aspects for testing
    ladder_obj = None
    if ladder:
        ladder_obj = Ladder.objects.create(code="TEST", name="Test Ladder")
        LadderAspect.objects.create(ladder=ladder_obj, code="DES", name="Design", order=1)
        LadderAspect.objects.create(ladder=ladder_obj, code="IMP", name="Implementation", order=2)

    note = Note.objects.create(
        owner=member,
        title="Note",
        content="...",
        date=timezone.now().date(),
        type=NoteType.GOAL,
        proposal_type=proposal_type,
    )
    
    aspect_changes = {}
    if ladder:
        aspect_changes = {"DES": {"changed": True, "new_level": 2}}
    
    Summary.objects.create(
        note=note,
        content="x",
        ladder=ladder_obj,
        aspect_changes=aspect_changes,
        salary_change=1 if salary else 0,
        bonus=10 if bonus else 0,
        submit_status=SummarySubmitStatus.DONE,
    )

    events = list(TimelineEvent.objects.filter(user=member).values_list("event_type", flat=True))
    assert set(events) == set(expected)


# ---------------------------------------------------------------------------
# Serializer fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_serializer_without_artefact_returns_nulls(settings, api_client, leader):
    """Manual TitleChange event returns null for object_url/model/object_id."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(leader)

    TitleChange.objects.create(
        user=leader,
        old_title="Engineer",
        new_title="Lead Engineer",
        effective_date=timezone.now().date(),
        created_by=leader,
    )

    url = reverse("api:user-timeline", args=[str(leader.uuid)])
    data = api_client.get(url).json()["results"][0]
    assert data["object_url"] is None
    assert data["model"] is None
    assert data["object_id"] is None


# ---------------------------------------------------------------------------
# Serializer – summary object_url
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_serializer_summary_has_object_url(settings, api_client, member):
    """Timeline event for Summary should include proper nested URL."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    # create note & summary
    note = Note.objects.create(
        owner=member,
        title="Review note",
        content="...",
        date=timezone.now().date(),
        type=NoteType.GOAL,
    )
    Summary.objects.create(
        note=note,
        content="x",
        bonus=5,
        ladder_change="",
        submit_status=SummarySubmitStatus.DONE,
    )

    url = reverse("api:user-timeline", args=[str(member.uuid)])
    data = api_client.get(url).json()["results"][0]
    assert data["model"] == "summary"
    assert data["object_url"] is not None
    frontend_path = f"/notes/{note.type.lower()}/{note.uuid}"
    assert frontend_path in data["object_url"]


# ---------------------------------------------------------------------------
# Maintainer write access
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_superuser_can_create_title_change(settings, api_client, member):
    """Superuser (maintainer) can POST /title-changes/ and receive 201."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    admin = User.objects.create_superuser("admin@example.com", "pw")
    api_client.force_authenticate(admin)

    url = reverse("api:title-changes-list")
    payload = {
        "user": member.pk,
        "old_title": "Developer",
        "new_title": "Senior Dev",
        "effective_date": str(timezone.now().date()),
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 201
    # Timeline event should be created
    assert TimelineEvent.objects.filter(user=member, event_type=EventType.TITLE_CHANGE).exists()


# ---------------------------------------------------------------------------
# Current level (SenioritySnapshot) util & API integration
# ---------------------------------------------------------------------------


@pytest.fixture
def member_snapshot(member):
    """Latest SenioritySnapshot for the member user."""
    # Create a ladder with aspects for proper testing
    ladder = Ladder.objects.create(code="SW", name="Software")
    LadderAspect.objects.create(ladder=ladder, code="DES", name="Design", order=1)
    LadderAspect.objects.create(ladder=ladder, code="IMP", name="Implementation", order=2)
    LadderAspect.objects.create(ladder=ladder, code="BUS", name="Business Acumen", order=3)
    LadderAspect.objects.create(ladder=ladder, code="COM", name="Communication", order=4)
    LadderAspect.objects.create(ladder=ladder, code="TL", name="Technical Leadership", order=5)
    
    return SenioritySnapshot.objects.create(
        user=member,
        ladder=ladder,
        title="",
        overall_score=2.4,
        details_json={
            "DES": 3,
            "IMP": 3,
            "BUS": 2,
            "COM": 2,
            "TL": 2,
        },
        effective_date=timezone.now().date(),
    )


# ---------------------------------------------------------------------------
# Ladder and SenioritySnapshot tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_get_current_level_returns_none_when_no_snapshot():
    """User without seniority snapshot returns None for current level."""
    from api.utils import get_current_level

    u = User.objects.create(email="plain@example.com", username="plain")
    assert get_current_level(u) is None


@pytest.mark.django_db
def test_get_current_level_returns_latest(member_snapshot, member):
    """User with seniority snapshot returns latest level data."""
    from api.utils import get_current_level

    data = get_current_level(member)
    assert data is not None
    assert data["overall"] == pytest.approx(2.4)
    assert data["details"]["Design"] == 3


@pytest.mark.django_db
def test_level_embedded_when_param_set(settings, api_client, member, member_snapshot):
    """Timeline includes level data when include_level parameter is set."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    url = reverse("api:user-timeline", args=[str(member.uuid)]) + "?include_level=true"
    resp = api_client.get(url)
    assert resp.status_code == 200
    body = resp.json()
    assert "level" in body
    assert body["level"]["overall"] == pytest.approx(2.4)


@pytest.mark.django_db
def test_level_not_embedded_without_param(settings, api_client, member, member_snapshot):
    """Timeline excludes level data when include_level parameter is not set."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    url = reverse("api:user-timeline", args=[str(member.uuid)])
    body = api_client.get(url).json()
    assert "level" not in body


@pytest.mark.django_db
def test_level_not_embedded_when_no_snapshot(settings, api_client, member):
    """Timeline excludes level data when user has no seniority snapshot."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    url = reverse("api:user-timeline", args=[str(member.uuid)]) + "?include_level=true"
    body = api_client.get(url).json()
    assert "level" not in body


# ────────────────────────────────────────────────────────────
# Current ladder endpoint & snapshot signal
# ────────────────────────────────────────────────────────────

import json
from api.models import Ladder, LadderAspect, SenioritySnapshot, Cycle, ProposalType, SummarySubmitStatus


def _create_ladder_with_aspects():
    """Create a test ladder with all 5 aspects for testing."""
    ladder = Ladder.objects.create(code="SW", name="Software")
    LadderAspect.objects.create(ladder=ladder, code="DES", name="Design", order=1)
    LadderAspect.objects.create(ladder=ladder, code="IMP", name="Implementation", order=2)
    LadderAspect.objects.create(ladder=ladder, code="BUS", name="Business Acumen", order=3)
    LadderAspect.objects.create(ladder=ladder, code="COM", name="Communication", order=4)
    LadderAspect.objects.create(ladder=ladder, code="TL", name="Technical Leadership", order=5)
    return ladder


@pytest.mark.django_db
def test_current_ladder_self(api_client, leader):
    """User can view their own current ladder information."""
    ladder = _create_ladder_with_aspects()
    SenioritySnapshot.objects.create(
        user=leader,
        ladder=ladder,
        overall_score=3,
        details_json={"DES": 3, "IMP": 3},
        effective_date=timezone.now().date(),
    )

    api_client.force_authenticate(leader)
    resp = api_client.get("/api/profile/current-ladder/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ladder"] == "SW"
    assert any(a["code"] == "DES" for a in data["aspects"])


@pytest.mark.django_db
def test_leader_can_view_subordinate_ladder(api_client, leader, member):
    """Leader can view subordinate's current ladder information."""
    ladder = _create_ladder_with_aspects()
    SenioritySnapshot.objects.create(
        user=member,
        ladder=ladder,
        overall_score=3,
        details_json={"DES": 3, "IMP": 3},
        effective_date=timezone.now().date(),
    )

    api_client.force_authenticate(leader)
    url = f"/api/profile/{member.uuid}/current-ladder/"
    assert api_client.get(url).status_code == 200


@pytest.mark.django_db
def test_unrelated_user_denied_current_ladder(api_client, leader, member):
    """Unrelated user cannot view another user's current ladder information."""
    stranger = User.objects.create(email="stranger@example.com", username="stranger")
    ladder = _create_ladder_with_aspects()
    SenioritySnapshot.objects.create(
        user=member,
        ladder=ladder,
        overall_score=3,
        details_json={},
        effective_date=timezone.now().date(),
    )
    api_client.force_authenticate(stranger)
    url = f"/api/profile/{member.uuid}/current-ladder/"
    assert api_client.get(url).status_code == 403


@pytest.mark.django_db
def test_summary_done_creates_snapshot(api_client, member):
    """Summary with DONE status creates seniority snapshot with all aspects."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    note = Note.objects.create(
        owner=member,
        title="Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 4}},
        salary_change=10,
        bonus=5,
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )

    snap = SenioritySnapshot.objects.filter(user=member, ladder=ladder).first()
    assert snap is not None
    # Should have all 5 aspects, with DES at level 4 (0+4) and others at default level 0
    assert snap.details_json.get("DES") == 4  # 0 + 4
    assert len(snap.details_json) == 5  # All 5 aspects should be present
    assert snap.details_json.get("IMP") == 0  # Other aspects should be at default level 0
    assert snap.details_json.get("BUS") == 0
    assert snap.details_json.get("COM") == 0
    assert snap.details_json.get("TL") == 0


@pytest.mark.django_db
def test_summary_merge_snapshot(api_client, member):
    """Summary merges aspect changes with existing snapshot data."""
    ladder = _create_ladder_with_aspects()
    today = timezone.now().date()
    cycle = Cycle.objects.create(name="C", start_date=timezone.now(), end_date=timezone.now())

    # existing snapshot with all 5 aspects at level 3
    SenioritySnapshot.objects.create(
        user=member,
        ladder=ladder,
        overall_score=3,
        details_json={"DES": 3, "IMP": 3, "BUS": 3, "COM": 3, "TL": 3},
        effective_date=today,
    )

    # new summary changes only DES -> 4
    note = Note.objects.create(
        owner=member,
        title="Proposal",
        content="…",
        date=today,
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 4}},
        salary_change=0,
        bonus=0,
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )

    snap = SenioritySnapshot.objects.filter(user=member, ladder=ladder).order_by("effective_date", "date_created").last()
    # Should preserve all 5 aspects, DES changed to 7 (3+4) and others remain at 3
    assert snap.details_json == {"DES": 7, "IMP": 3, "BUS": 3, "COM": 3, "TL": 3}
    # Overall score should be (7+3+3+3+3)/5 = 3.8
    assert snap.overall_score == 3.8


# ---------------------------------------------------------------------------
# Level Addition Logic Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_level_addition_logic(api_client, member):
    """Test that level changes are added to existing levels, not replaced."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    # First summary: set DES to level 3
    note1 = Note.objects.create(
        owner=member,
        title="First Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note1,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 3}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Second summary: add 2 more to DES (should become 5)
    note2 = Note.objects.create(
        owner=member,
        title="Second Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note2,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 2}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    snap = SenioritySnapshot.objects.filter(user=member, ladder=ladder).order_by("effective_date", "date_created").last()
    # DES should be 3 + 2 = 5, others should remain at 0
    assert snap.details_json.get("DES") == 5
    assert snap.details_json.get("IMP") == 0
    assert snap.overall_score == 1.0  # (5+0+0+0+0)/5 = 1.0


@pytest.mark.django_db
def test_timeline_text_with_change_amounts(api_client, member):
    """Test that timeline text shows change amounts correctly."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    note = Note.objects.create(
        owner=member,
        title="Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 3}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    event = TimelineEvent.objects.filter(user=member, event_type=EventType.SENIORITY_CHANGE).first()
    assert event is not None
    # Should show the change amount in the text
    assert "(+3)" in event.summary_text


@pytest.mark.django_db
def test_mapping_with_salary_change(api_client, member):
    """Test that MAPPING proposals can trigger salary change events."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    note = Note.objects.create(
        owner=member,
        title="Mapping Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.MAPPING,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 2}},
        salary_change=5,
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    events = TimelineEvent.objects.filter(user=member)
    event_types = [event.event_type for event in events]
    
    # Should have both MAPPING and PAY_CHANGE events
    assert EventType.MAPPING in event_types
    assert EventType.PAY_CHANGE in event_types


@pytest.mark.django_db
def test_ladder_change_detection(api_client, member):
    """Test that ladder changes create LADDER_CHANGED timeline events."""
    # Create two different ladders with unique codes
    ladder1 = Ladder.objects.create(code="TEST1", name="Test Ladder 1")
    LadderAspect.objects.create(ladder=ladder1, code="DES", name="Design", order=1)
    LadderAspect.objects.create(ladder=ladder1, code="IMP", name="Implementation", order=2)
    
    ladder2 = Ladder.objects.create(code="TEST2", name="Test Ladder 2")
    LadderAspect.objects.create(ladder=ladder2, code="STR", name="Strategy", order=1)
    LadderAspect.objects.create(ladder=ladder2, code="EXE", name="Execution", order=2)
    
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    # Create first summary with ladder1 - this creates the first snapshot
    note1 = Note.objects.create(
        owner=member,
        title="First Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note1,
        ladder=ladder1,
        aspect_changes={"DES": {"changed": True, "new_level": 2}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Verify first snapshot was created with ladder1
    first_snapshot = SenioritySnapshot.objects.filter(user=member).first()
    assert first_snapshot is not None
    assert first_snapshot.ladder == ladder1
    
    # Create second summary with ladder2 (different ladder) - this should trigger LADDER_CHANGED
    note2 = Note.objects.create(
        owner=member,
        title="Second Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note2,
        ladder=ladder2,
        aspect_changes={"STR": {"changed": True, "new_level": 1}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Check that LADDER_CHANGED event was created
    ladder_change_event = TimelineEvent.objects.filter(
        user=member, 
        event_type=EventType.LADDER_CHANGED
    ).first()
    
    assert ladder_change_event is not None
    assert "Test Ladder 1" in ladder_change_event.summary_text
    assert "Test Ladder 2" in ladder_change_event.summary_text
    assert "تغییر لدر کاربر" in ladder_change_event.summary_text
    
    # Verify second snapshot was created with ladder2
    second_snapshot = SenioritySnapshot.objects.filter(user=member).order_by('effective_date', 'date_created').last()
    assert second_snapshot.ladder == ladder2


@pytest.mark.django_db
def test_no_ladder_change_event_for_same_ladder(api_client, member):
    """Test that LADDER_CHANGED event is not created when ladder doesn't change."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    # Create first summary
    note1 = Note.objects.create(
        owner=member,
        title="First Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note1,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 2}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Create second summary with same ladder
    note2 = Note.objects.create(
        owner=member,
        title="Second Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note2,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 1}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Check that no LADDER_CHANGED event was created
    ladder_change_events = TimelineEvent.objects.filter(
        user=member, 
        event_type=EventType.LADDER_CHANGED
    )
    
    assert ladder_change_events.count() == 0


@pytest.mark.django_db
def test_ladder_change_event_with_no_previous_snapshot(api_client, member):
    """Test that LADDER_CHANGED event is not created when there's no previous snapshot."""
    ladder = _create_ladder_with_aspects()
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    # Create first summary (no previous snapshot exists)
    note = Note.objects.create(
        owner=member,
        title="First Proposal",
        content="…",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note,
        ladder=ladder,
        aspect_changes={"DES": {"changed": True, "new_level": 2}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Check that no LADDER_CHANGED event was created (no previous snapshot to compare against)
    ladder_change_events = TimelineEvent.objects.filter(
        user=member, 
        event_type=EventType.LADDER_CHANGED
    )
    
    assert ladder_change_events.count() == 0


@pytest.mark.django_db
def test_ladder_switching_with_level_preservation(api_client, member):
    """Test ladder switching scenario with level preservation and restoration."""
    # Create two different ladders with different aspects
    ladder1 = Ladder.objects.create(code="SWITCH1", name="Switch Ladder 1")
    LadderAspect.objects.create(ladder=ladder1, code="ASP1", name="Aspect 1", order=1)
    LadderAspect.objects.create(ladder=ladder1, code="ASP2", name="Aspect 2", order=2)
    LadderAspect.objects.create(ladder=ladder1, code="ASP3", name="Aspect 3", order=3)
    LadderAspect.objects.create(ladder=ladder1, code="ASP4", name="Aspect 4", order=4)
    
    ladder2 = Ladder.objects.create(code="SWITCH2", name="Switch Ladder 2")
    LadderAspect.objects.create(ladder=ladder2, code="STR", name="Strategy", order=1)
    LadderAspect.objects.create(ladder=ladder2, code="EXE", name="Execution", order=2)
    LadderAspect.objects.create(ladder=ladder2, code="USR", name="User Research", order=3)
    
    cycle = Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now())
    
    # Step 1: Create initial levels on Ladder 1
    note1 = Note.objects.create(
        owner=member,
        title="Initial Ladder 1 Proposal",
        content="Setting initial levels on Ladder 1",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note1,
        ladder=ladder1,
        aspect_changes={
            "ASP1": {"changed": True, "new_level": 1},
            "ASP2": {"changed": True, "new_level": 2},
            "ASP3": {"changed": True, "new_level": 1},
            "ASP4": {"changed": True, "new_level": 2},
        },
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Verify initial snapshot on Ladder 1
    snapshot1 = SenioritySnapshot.objects.filter(user=member, ladder=ladder1).first()
    assert snapshot1 is not None
    assert snapshot1.details_json == {"ASP1": 1, "ASP2": 2, "ASP3": 1, "ASP4": 2}
    assert snapshot1.overall_score == 1.5  # (1+2+1+2)/4 = 1.5
    
    # Step 2: Switch to Ladder 2 and set new levels
    note2 = Note.objects.create(
        owner=member,
        title="Switch to Ladder 2",
        content="Switching to Product Ladder",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note2,
        ladder=ladder2,
        aspect_changes={
            "STR": {"changed": True, "new_level": 3},
            "EXE": {"changed": True, "new_level": 2},
            "USR": {"changed": True, "new_level": 1},
        },
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
        # Verify LADDER_CHANGED event was created
    ladder_change_event = TimelineEvent.objects.filter(
        user=member,
        event_type=EventType.LADDER_CHANGED
    ).first()
    assert ladder_change_event is not None
    assert "Switch Ladder 1" in ladder_change_event.summary_text
    assert "Switch Ladder 2" in ladder_change_event.summary_text
    
    # Verify new snapshot on Ladder 2
    snapshot2 = SenioritySnapshot.objects.filter(user=member, ladder=ladder2).first()
    assert snapshot2 is not None
    assert snapshot2.details_json == {"STR": 3, "EXE": 2, "USR": 1}
    assert snapshot2.overall_score == 2.0  # (3+2+1)/3 = 2.0
    
    # Verify Ladder 1 snapshot still exists and unchanged
    snapshot1_after = SenioritySnapshot.objects.filter(user=member, ladder=ladder1).first()
    assert snapshot1_after.details_json == {"ASP1": 1, "ASP2": 2, "ASP3": 1, "ASP4": 2}
    
    # Step 3: Switch back to Ladder 1 and add 1 point to all aspects
    note3 = Note.objects.create(
        owner=member,
        title="Back to Ladder 1",
        content="Returning to Software Ladder and adding 1 to all aspects",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=cycle,
    )
    Summary.objects.create(
        note=note3,
        ladder=ladder1,
        aspect_changes={
            "ASP1": {"changed": True, "new_level": 1},  # 1 + 1 = 2
            "ASP2": {"changed": True, "new_level": 1},  # 2 + 1 = 3
            "ASP3": {"changed": True, "new_level": 1},  # 1 + 1 = 2
            "ASP4": {"changed": True, "new_level": 1},  # 2 + 1 = 3
        },
        submit_status=SummarySubmitStatus.DONE,
        cycle=cycle,
    )
    
    # Verify second LADDER_CHANGED event was created
    ladder_change_events = TimelineEvent.objects.filter(
        user=member, 
        event_type=EventType.LADDER_CHANGED
    )
    assert ladder_change_events.count() == 2
    
    # Verify updated snapshot on Ladder 1 (levels should be added to previous levels)
    snapshot1_updated = SenioritySnapshot.objects.filter(user=member, ladder=ladder1).order_by("effective_date", "date_created").last()
    assert snapshot1_updated.details_json == {"ASP1": 2, "ASP2": 3, "ASP3": 2, "ASP4": 3}
    assert snapshot1_updated.overall_score == 2.5  # (2+3+2+3)/4 = 2.5
    
    # Verify Ladder 2 snapshot still exists and unchanged
    snapshot2_after = SenioritySnapshot.objects.filter(user=member, ladder=ladder2).first()
    assert snapshot2_after.details_json == {"STR": 3, "EXE": 2, "USR": 1}
    
    # Verify timeline events show the correct ladder information
    seniority_events = TimelineEvent.objects.filter(
        user=member, 
        event_type=EventType.SENIORITY_CHANGE
    ).order_by('effective_date')
    
    # First seniority event should show Ladder 1 aspects
    assert len(seniority_events) >= 2
    first_seniority_event = seniority_events[0]
    assert "Aspect 1" in first_seniority_event.summary_text or "ASP1" in first_seniority_event.summary_text
    
    # Second seniority event should show Ladder 2 aspects
    second_seniority_event = seniority_events[1]
    assert "Strategy" in second_seniority_event.summary_text or "STR" in second_seniority_event.summary_text
    
    # Third seniority event should show Ladder 1 aspects again
    third_seniority_event = seniority_events[2]
    assert "Aspect 1" in third_seniority_event.summary_text or "ASP1" in third_seniority_event.summary_text


# ---------------------------------------------------------------------------
# Object URL Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_object_url_for_note_localhost(api_client, member):
    """Test object_url generation for note in localhost environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Note).id,
        object_id=note.id,
        created_by=member,
    )
    
    # Create request with localhost host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to localhost frontend
    assert data['object_url'] is not None
    assert 'http://localhost:3000' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_note_staging(api_client, member):
    """Test object_url generation for note in staging environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Note).id,
        object_id=note.id,
        created_by=member,
    )
    
    # Create request with staging host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'st.merlin.sotoon.ir'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to staging frontend
    assert data['object_url'] is not None
    assert 'https://st.merlin.sotoon.ir' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_note_production(api_client, member):
    """Test object_url generation for note in production environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Note).id,
        object_id=note.id,
        created_by=member,
    )
    
    # Create request with production host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'merlin.sotoon.ir'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to production frontend
    assert data['object_url'] is not None
    assert 'https://merlin.sotoon.ir' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_summary_localhost(api_client, member):
    """Test object_url generation for summary in localhost environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create a summary
    summary = Summary.objects.create(
        note=note,
        content="Test summary",
        ladder=_create_ladder_with_aspects(),
        aspect_changes={"DES": {"changed": True, "new_level": 4}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Summary).id,
        object_id=summary.id,
        created_by=member,
    )
    
    # Create request with localhost host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to localhost frontend and uses note's type
    assert data['object_url'] is not None
    assert 'http://localhost:3000' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_summary_staging(api_client, member):
    """Test object_url generation for summary in staging environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create a summary
    summary = Summary.objects.create(
        note=note,
        content="Test summary",
        ladder=_create_ladder_with_aspects(),
        aspect_changes={"DES": {"changed": True, "new_level": 4}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Summary).id,
        object_id=summary.id,
        created_by=member,
    )
    
    # Create request with staging host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'st.merlin.sotoon.ir'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to staging frontend
    assert data['object_url'] is not None
    assert 'https://st.merlin.sotoon.ir' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_summary_production(api_client, member):
    """Test object_url generation for summary in production environment."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create a summary
    summary = Summary.objects.create(
        note=note,
        content="Test summary",
        ladder=_create_ladder_with_aspects(),
        aspect_changes={"DES": {"changed": True, "new_level": 4}},
        submit_status=SummarySubmitStatus.DONE,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Summary).id,
        object_id=summary.id,
        created_by=member,
    )
    
    # Create request with production host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'merlin.sotoon.ir'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Check that object_url points to production frontend
    assert data['object_url'] is not None
    assert 'https://merlin.sotoon.ir' in data['object_url']
    assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_without_request_context(api_client, member):
    """Test object_url generation without request context (should fallback)."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    # Create a note
    note = Note.objects.create(
        owner=member,
        title="Test Proposal",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.Proposal,
        proposal_type=ProposalType.PROMOTION,
        cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
    )
    
    # Create timeline event
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Note).id,
        object_id=note.id,
        created_by=member,
    )
    
    # Serialize without request context
    serializer = TimelineEventLiteSerializer(event)
    data = serializer.data
    
    # Should fallback to API URL when no request context
    assert data['object_url'] is not None
    assert '/api/notes/' in data['object_url']


@pytest.mark.django_db
def test_object_url_for_different_note_types(api_client, member):
    """Test object_url generation for different note types."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    note_types = [
        NoteType.Proposal,
        NoteType.GOAL,
        NoteType.ONE_ON_ONE,
        NoteType.MEETING,
    ]
    
    for note_type in note_types:
        # Create a note
        note = Note.objects.create(
            owner=member,
            title=f"Test {note_type}",
            content="Test content",
            date=timezone.now().date(),
            type=note_type,
            proposal_type=ProposalType.PROMOTION if note_type == NoteType.Proposal else ProposalType.PROMOTION,  # All notes need proposal_type
            cycle=Cycle.objects.create(name="Test", start_date=timezone.now(), end_date=timezone.now()),
        )
        
        # Create timeline event
        event = TimelineEvent.objects.create(
            user=member,
            event_type=EventType.SENIORITY_CHANGE,
            summary_text="Test event",
            effective_date=timezone.now().date(),
            content_type_id=ContentType.objects.get_for_model(Note).id,
            object_id=note.id,
            created_by=member,
        )
        
        # Create request with localhost host
        request = factory.get('/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        
        # Serialize with request context
        serializer = TimelineEventLiteSerializer(event, context={'request': request})
        data = serializer.data
        
        # Check that object_url uses correct note type
        assert data['object_url'] is not None
        assert f'/notes/{note.type.lower()}/{note.uuid}' in data['object_url']


@pytest.mark.django_db
def test_object_url_with_exception_handling(api_client, member):
    """Test object_url generation when object lookup fails."""
    from django.test import RequestFactory
    from api.serializers.timeline import TimelineEventLiteSerializer
    
    factory = RequestFactory()
    
    # Create timeline event with non-existent object_id
    event = TimelineEvent.objects.create(
        user=member,
        event_type=EventType.SENIORITY_CHANGE,
        summary_text="Test event",
        effective_date=timezone.now().date(),
        content_type_id=ContentType.objects.get_for_model(Note).id,
        object_id=99999,  # Non-existent ID
        created_by=member,
    )
    
    # Create request with localhost host
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Serialize with request context
    serializer = TimelineEventLiteSerializer(event, context={'request': request})
    data = serializer.data
    
    # Should handle exception gracefully and return a URL (even for non-existent objects)
    assert data['object_url'] is not None
    assert '/api/notes/' in data['object_url']


@pytest.mark.django_db
def test_ladder_max_level_calculation(api_client, leader):
    """Test that ladder max_level is correctly calculated from LadderLevel objects."""
    # Create Software ladder with 6 levels
    sw_ladder = Ladder.objects.create(code="SW", name="Software")
    sw_aspect = LadderAspect.objects.create(ladder=sw_ladder, code="DES", name="Design", order=1)
    
    # Create levels 1-6 for Software ladder
    for level in range(1, 7):
        LadderLevel.objects.create(
            ladder=sw_ladder,
            aspect=sw_aspect,
            level=level,
            stage=LadderStage.EARLY
        )
    
    # Create Product ladder with 7 levels
    pd_ladder = Ladder.objects.create(code="PD", name="Product")
    pd_aspect = LadderAspect.objects.create(ladder=pd_ladder, code="STR", name="Strategy", order=1)
    
    # Create levels 1-7 for Product ladder
    for level in range(1, 8):
        LadderLevel.objects.create(
            ladder=pd_ladder,
            aspect=pd_aspect,
            level=level,
            stage=LadderStage.EARLY
        )
    
    # Test get_max_level method
    assert sw_ladder.get_max_level() == 6
    assert pd_ladder.get_max_level() == 7
    
    # Create a snapshot for the leader with Software ladder so the API returns the correct ladder
    SenioritySnapshot.objects.create(
        user=leader,
        ladder=sw_ladder,
        overall_score=3.0,
        details_json={"DES": 3},
        effective_date=timezone.now().date(),
    )
    
    # Test current ladder API includes max_level
    api_client.force_authenticate(leader)
    resp = api_client.get("/api/profile/current-ladder/")
    assert resp.status_code == 200
    data = resp.json()
    assert "max_level" in data
    assert data["max_level"] == 6  # Should return Software ladder's max_level
    
    # Test ladder list API includes max_level
    resp = api_client.get("/api/ladders/")
    assert resp.status_code == 200
    data = resp.json()
    
    # Find Software and Product ladders in response
    sw_ladder_data = next((l for l in data if l["code"] == "SW"), None)
    pd_ladder_data = next((l for l in data if l["code"] == "PD"), None)
    
    assert sw_ladder_data is not None
    assert pd_ladder_data is not None
    assert sw_ladder_data["max_level"] == 6
    assert pd_ladder_data["max_level"] == 7


@pytest.mark.django_db
def test_ladder_max_level_with_no_levels(api_client, leader):
    """Test that ladder max_level returns 0 when no levels exist."""
    # Create ladder without any levels
    ladder = Ladder.objects.create(code="TEST", name="Test Ladder")
    LadderAspect.objects.create(ladder=ladder, code="ASP", name="Aspect", order=1)
    
    # Test get_max_level returns 0
    assert ladder.get_max_level() == 0
    
    # Test API includes max_level as 0
    api_client.force_authenticate(leader)
    resp = api_client.get("/api/ladders/")
    assert resp.status_code == 200
    data = resp.json()
    
    test_ladder_data = next((l for l in data if l["code"] == "TEST"), None)
    assert test_ladder_data is not None
    assert test_ladder_data["max_level"] == 0