import pytest
from django.urls import reverse
from django.utils import timezone

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
    ProposalType
)


# ---------------------------------------------------------------------------
# Factories (minimal inline factory_boy-style helpers)
# ---------------------------------------------------------------------------


@pytest.fixture
def department(db):
    return Department.objects.create(name="Engineering")


@pytest.fixture
def tribe(department):
    return Tribe.objects.create(name="Backend", department=department)


@pytest.fixture
def team(tribe, department):
    return Team.objects.create(name="API", tribe=tribe, department=department)


@pytest.fixture
def leader(db):
    return User.objects.create(email="leader@example.com", username="leader")


@pytest.fixture
def member(team, leader):
    return User.objects.create(
        email="member@example.com",
        username="member",
        leader=leader,
        team=team,
    )


# Note: Committee currently has no type field.
@pytest.fixture
def committee(db):
    return Committee.objects.create(name="Eval-Com")


@pytest.fixture
def summary(member):
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
    # URL should include both note id and summary id segments
    assert f"/notes/{note.id}/summaries/" in data["object_url"]


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


@pytest.mark.django_db
def test_get_current_level_returns_none_when_no_snapshot():
    from api.utils import get_current_level

    u = User.objects.create(email="plain@example.com", username="plain")
    assert get_current_level(u) is None


@pytest.mark.django_db
def test_get_current_level_returns_latest(member_snapshot, member):
    from api.utils import get_current_level

    data = get_current_level(member)
    assert data is not None
    assert data["overall"] == pytest.approx(2.4)
    assert data["details"]["Design"] == 3


@pytest.mark.django_db
def test_level_embedded_when_param_set(settings, api_client, member, member_snapshot):
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
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    url = reverse("api:user-timeline", args=[str(member.uuid)])
    body = api_client.get(url).json()
    assert "level" not in body


@pytest.mark.django_db
def test_level_not_embedded_when_no_snapshot(settings, api_client, member):
    settings.FEATURE_CAREER_TIMELINE_ACCESS = "all"
    api_client.force_authenticate(member)

    url = reverse("api:user-timeline", args=[str(member.uuid)]) + "?include_level=true"
    body = api_client.get(url).json()
    assert "level" not in body