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
    LadderAspect
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
    "proposal_type, ladder, salary, expected",
    [
        (ProposalType.EVALUATION, True, True, [EventType.EVALUATION]),
        (ProposalType.PROMOTION, True, False, [EventType.SENIORITY_CHANGE]),
        (ProposalType.PROMOTION, False, True, [EventType.PAY_CHANGE]),
        (ProposalType.PROMOTION, True, True, [EventType.SENIORITY_CHANGE, EventType.PAY_CHANGE]),
        (ProposalType.MAPPING, False, False, [EventType.MAPPING]),
        (ProposalType.NOTICE, False, False, [EventType.NOTICE]),
    ],
)
@pytest.mark.django_db
def test_summary_generates_correct_events(settings, proposal_type, ladder, salary, expected, member):
    """Summary DONE emits correct TimelineEvent(s) per committee type and data fields."""
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"

    committee = Committee.objects.create(name="C")
    member.committee = committee
    member.save()

    note = Note.objects.create(
        owner=member,
        title="Note",
        content="...",
        date=timezone.now().date(),
        type=NoteType.GOAL,
        proposal_type=proposal_type,
    )
    Summary.objects.create(
        note=note,
        content="x",
        ladder_change="LvUp" if ladder else "",
        salary_change=1 if salary else 0,
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
    return SenioritySnapshot.objects.create(
        user=member,
        title="",
        overall_score=2.4,
        details_json={
            "Design": 3,
            "Implementation": 3,
            "Business Acumen": 2,
            "Communication": 2,
            "Technical Lead": 2,
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
    # Should have all 5 aspects, with DES at level 4 and others at default level 3
    assert snap.details_json.get("DES") == 4
    assert len(snap.details_json) == 5  # All 5 aspects should be present
    assert snap.details_json.get("IMP") == 3  # Other aspects should be at default level
    assert snap.details_json.get("BUS") == 3
    assert snap.details_json.get("COM") == 3
    assert snap.details_json.get("TL") == 3


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

    snap = SenioritySnapshot.objects.filter(user=member, ladder=ladder).latest("effective_date")
    # Should preserve all 5 aspects, only DES changed to 4
    assert snap.details_json == {"DES": 4, "IMP": 3, "BUS": 3, "COM": 3, "TL": 3}
    # Overall score should be (4+3+3+3+3)/5 = 3.2
    assert snap.overall_score == 3.2


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