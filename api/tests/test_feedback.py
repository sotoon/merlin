import pytest
import uuid
import factory
from pytest_factoryboy import register
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.utils import timezone

from api.models import (
    User,
    FeedbackForm,
    Feedback,
    FeedbackRequest,
    FeedbackRequestUserLink,
    Cycle,
    Note,
    NoteType,
    NoteUserAccess,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@sotoon.ir")
    password = factory.PostGenerationMethodCall("set_password", "pw")
    name = factory.Faker("name")


class FeedbackFormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeedbackForm

    title = factory.Sequence(lambda n: f"Form {n}")
    description = "Sample form"
    is_active = True
    schema = {}


class CycleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cycle

    name = factory.Sequence(lambda n: f"Cycle-{n}")
    start_date = factory.LazyFunction(lambda: timezone.now())
    end_date = factory.LazyFunction(lambda: timezone.now())
    is_active = True


register(UserFactory)
register(UserFactory, "receiver")
register(UserFactory, "outsider")
register(FeedbackFormFactory)
register(CycleFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def _current_cycle():
    """Ensure an active cycle exists for all feedback tests."""
    return CycleFactory()


# ──────────────────────────────────────────────────
# Feedback Request flow
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_requester_can_create_feedback_request(
    api_client, user, receiver, feedback_form_factory
):
    """Requester creates a feedback request; link rows & ACL for invitee created."""
    form = feedback_form_factory()
    api_client.force_authenticate(user)
    payload = {
        "title": "Need feedback",
        "content": "Please give me feedback on project X",
        "requestee_emails": [receiver.email],
        "form_uuid": str(form.uuid),
    }
    url = reverse("api:feedback-requests-list")
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    fr_uuid = resp.data["uuid"]
    fr = FeedbackRequest.objects.get(uuid=fr_uuid)
    assert fr.requestees.filter(user=receiver).exists()


@pytest.mark.django_db
def test_only_owner_sees_own_requests(api_client, user, receiver):
    """Owner can retrieve their request; invitee can view too; others 404."""
    # user creates request
    api_client.force_authenticate(user)
    payload = {
        "title": "Need feedback",
        "content": "content",
        "requestee_emails": [receiver.email],
    }
    url = reverse("api:feedback-requests-list")
    fr_resp = api_client.post(url, payload, format="json")
    fr_uuid = fr_resp.data["uuid"]

    # owner can GET detail
    detail_url = reverse("api:feedback-requests-detail", kwargs={"uuid": fr_uuid})
    assert api_client.get(detail_url).status_code == 200

    # receiver can view (safe)
    api_client.force_authenticate(receiver)
    assert api_client.get(detail_url).status_code == 200


@pytest.mark.django_db
def test_outsider_cannot_view_request(api_client, user, receiver, outsider):
    """Unrelated outsider gets 403/404 on request detail."""
    api_client.force_authenticate(user)
    url = reverse("api:feedback-requests-list")
    fr_uuid = api_client.post(
        url,
        {
            "title": "Need feedback",
            "content": "x",
            "requestee_emails": [receiver.email],
        },
        format="json",
    ).data["uuid"]

    detail_url = reverse("api:feedback-requests-detail", kwargs={"uuid": fr_uuid})
    api_client.force_authenticate(outsider)
    assert api_client.get(detail_url).status_code in (403, 404)


# ──────────────────────────────────────────────────
# Feedback Entry flow
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_sender_can_send_feedback(api_client, user, receiver):
    """Sender posts ad-hoc feedback; sender & receiver can read entry."""
    api_client.force_authenticate(user)
    payload = {
        "receiver_ids": [str(receiver.uuid)],
        "content": "Great work!",
        "evidence": "PR #123",
    }
    url = reverse("api:feedback-entries-list")
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    uuid = resp.data["uuid"]

    # sender and receiver can GET
    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": uuid})
    assert api_client.get(detail_url).status_code == 200

    api_client.force_authenticate(receiver)
    assert api_client.get(detail_url).status_code == 200

    api_client.force_authenticate(user)  # owner/requester
    assert api_client.get(detail_url).status_code == 200


@pytest.mark.django_db
def test_outsider_cannot_access_feedback(api_client, user, receiver, outsider):
    """Outsider must not view someone else's feedback entry."""
    api_client.force_authenticate(user)
    uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "Hi",
        },
        format="json",
    ).data["uuid"]

    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": uuid})
    api_client.force_authenticate(outsider)
    assert api_client.get(detail_url).status_code in (403, 404)


# ──────────────────────────────────────────────────
# Privacy between feedback givers
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_second_sender_cannot_see_others_feedback(api_client, user_factory):
    """Two senders to same receiver should not see each other's feedback."""
    receiver = user_factory()
    sender1 = user_factory()
    sender2 = user_factory()

    # sender1 → receiver
    api_client.force_authenticate(sender1)
    fb1_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "fb1",
        },
        format="json",
    ).data["uuid"]

    # sender2 → receiver
    api_client.force_authenticate(sender2)
    fb2_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "fb2",
        },
        format="json",
    ).data["uuid"]

    # sender1 should NOT see fb2
    api_client.force_authenticate(sender1)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid})
    )
    assert resp.status_code in (403, 404)

    # sender2 should NOT see fb1
    api_client.force_authenticate(sender2)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb1_uuid})
    )
    assert resp.status_code in (403, 404)

    # receiver can see both
    api_client.force_authenticate(receiver)
    assert (
        api_client.get(
            reverse("api:feedback-entries-detail", kwargs={"uuid": fb1_uuid})
        ).status_code
        == 200
    )
    assert (
        api_client.get(
            reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid})
        ).status_code
        == 200
    )


# ──────────────────────────────────────────────────
# Mentioned users access
# ──────────────────────────────────────────────────


@pytest.fixture
def mentioned_user(user_factory):
    """User who will be mentioned in feedback notes."""
    return user_factory()


@pytest.mark.django_db
def test_mentioned_user_can_view_ad_hoc_feedback(
    api_client, user, receiver, mentioned_user
):
    """Mentioned users should gain view access to ad-hoc feedback entries (no request linkage)."""
    # Sender (user) creates ad-hoc feedback for receiver
    api_client.force_authenticate(user)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "Great collaboration @%s" % mentioned_user.email,
        },
        format="json",
    ).data["uuid"]

    # Server-side simulation: add mention link (UI would do this)
    fb = Feedback.objects.get(uuid=fb_uuid)
    fb.note.mentioned_users.add(mentioned_user)

    # Mentioned user should be able to read feedback
    api_client.force_authenticate(mentioned_user)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_mentioned_user_cannot_view_request_answer(
    api_client, user, receiver, mentioned_user
):
    """Mentioned users must NOT see feedback answers tied to a request (privacy)."""
    # Step 1: user sends request to receiver
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need feedback",
            "content": "Please give me feedback",
            "requestee_emails": [receiver.email],
        },
        format="json",
    ).data["uuid"]

    # Step 2: receiver answers the request (creates feedback entry)
    api_client.force_authenticate(receiver)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "Here's my feedback @%s" % mentioned_user.email,
        },
        format="json",
    ).data["uuid"]

    # Add mention
    fb = Feedback.objects.get(uuid=fb_uuid)
    fb.note.mentioned_users.add(mentioned_user)

    # Mentioned user should be denied access
    api_client.force_authenticate(mentioned_user)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


# ──────────────────────────────────────────────────
# Additional edge-case & regression tests
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_past_deadline_rejected(api_client, user, receiver):
    """Creating a feedback request with a past deadline must return 400."""
    api_client.force_authenticate(user)
    payload = {
        "title": "Past deadline",
        "content": "x",
        "requestee_emails": [receiver.email],
        "deadline": str((timezone.now() - timezone.timedelta(days=1)).date()),
    }
    resp = api_client.post(
        reverse("api:feedback-requests-list"), payload, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_self_invite_filtered(api_client, user):
    """Owner listed in requestee_emails should not receive a FeedbackRequestUserLink."""
    api_client.force_authenticate(user)
    resp = api_client.post(
        reverse("api:feedback-requests-list"),
        {"title": "Need feedback", "content": "x", "requestee_emails": [user.email]},
        format="json",
    )
    # Self-invite must be rejected outright
    assert resp.status_code == status.HTTP_400_BAD_REQUEST



@pytest.mark.django_db
def test_invalid_form_uuid(api_client, user, receiver):
    """Submitting an unknown form_uuid should raise validation error 400."""
    api_client.force_authenticate(user)
    payload = {
        "title": "invalid form",
        "content": "x",
        "requestee_emails": [receiver.email],
        "form_uuid": str(uuid.uuid4()),
    }
    resp = api_client.post(
        reverse("api:feedback-requests-list"), payload, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_uninvited_cannot_answer(api_client, user, receiver, outsider):
    """A user not invited to a request must not be able to answer it."""
    # Owner creates request
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {"title": "Need fb", "content": "x", "requestee_emails": [receiver.email]},
        format="json",
    ).data["uuid"]

    # Outsider attempts to answer
    api_client.force_authenticate(outsider)
    resp = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "I'm not invited",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_receiver_must_be_owner(api_client, user, receiver, outsider):
    """Answer payload must set receiver to request owner only."""
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {"title": "Need fb", "content": "x", "requestee_emails": [receiver.email]},
        format="json",
    ).data["uuid"]

    api_client.force_authenticate(receiver)
    resp = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],  # wrong receiver
            "feedback_request_uuid": str(fr_uuid),
            "content": "bad receiver",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_self_feedback_blocked(api_client, user):
    """Sending ad-hoc feedback to oneself must be rejected."""
    api_client.force_authenticate(user)
    resp = api_client.post(
        reverse("api:feedback-entries-list"),
        {"receiver_ids": [str(user.uuid)], "content": "to myself"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_answered_flag_set(api_client, user, receiver):
    """After an invitee answers, FeedbackRequestUserLink.answered should be True."""
    # Owner invites receiver
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {"title": "Need fb", "content": "x", "requestee_emails": [receiver.email]},
        format="json",
    ).data["uuid"]

    # Receiver answers
    api_client.force_authenticate(receiver)
    api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "here",
        },
        format="json",
    )

    link = FeedbackRequestUserLink.objects.get(request__uuid=fr_uuid, user=receiver)
    assert link.answered is True


@pytest.mark.django_db
def test_request_owner_sees_all_answers(api_client, user, receiver, outsider):
    """Request owner should be able to read every answer submitted."""
    # Owner creates request with two invitees
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need fb",
            "content": "x",
            "requestee_emails": [receiver.email, outsider.email],
        },
        format="json",
    ).data["uuid"]

    # Both invitees submit answers
    api_client.force_authenticate(receiver)
    fb1_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "r1",
        },
        format="json",
    ).data["uuid"]

    api_client.force_authenticate(outsider)
    fb2_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "r2",
        },
        format="json",
    ).data["uuid"]

    # Owner can read both answers
    api_client.force_authenticate(user)
    for fb_uuid in (fb1_uuid, fb2_uuid):
        detail = reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
        assert api_client.get(detail).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_mention_does_not_unlock_request_answer(api_client, user, receiver, outsider):
    """Being mentioned in an answer should not override privacy for other invitees."""
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need fb",
            "content": "x",
            "requestee_emails": [receiver.email, outsider.email],
        },
        format="json",
    ).data["uuid"]

    api_client.force_authenticate(receiver)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": f"ping @{outsider.email}",
        },
        format="json",
    ).data["uuid"]
    fb = Feedback.objects.get(uuid=fb_uuid)
    fb.note.mentioned_users.add(outsider)

    # Outsider still cannot read receiver's answer
    api_client.force_authenticate(outsider)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
def test_permissions_update_delete(api_client, user, receiver, outsider):
    """Only sender may PATCH or DELETE their feedback; others receive 403/404."""
    # Sender creates entry
    api_client.force_authenticate(user)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {"receiver_ids": [str(receiver.uuid)], "content": "hi"},
        format="json",
    ).data["uuid"]
    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})

    # Sender can PATCH and DELETE
    assert (
        api_client.patch(detail_url, {"content": "edit"}, format="json").status_code
        == 200
    )
    assert api_client.delete(detail_url).status_code == 204

    # Recreate for negative checks
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {"receiver_ids": [str(receiver.uuid)], "content": "hi2"},
        format="json",
    ).data["uuid"]
    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})

    api_client.force_authenticate(receiver)
    assert api_client.delete(detail_url).status_code in (403, 404)

    api_client.force_authenticate(outsider)
    assert api_client.patch(
        detail_url, {"content": "x"}, format="json"
    ).status_code in (
        403,
        404,
    )


@pytest.mark.django_db
def test_inactive_form_rejected(api_client, user, receiver, feedback_form_factory):
    """Using an inactive FeedbackForm must be rejected with 400."""
    inactive_form: FeedbackForm = feedback_form_factory(is_active=False)
    api_client.force_authenticate(user)
    resp = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "form_uuid": str(inactive_form.uuid),
            "content": "x",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ──────────────────────────────────────────────────
# List endpoints: /feedback-requests/ with type filter
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_owned_and_invited_filters_separate(api_client, user_factory):
    """
    The "type=owned" filter must return only requests created by the caller,
    while the "type=invited" filter must return only requests where the caller
    is an invitee (and not the owner).
    """
    owner = user_factory()  # will own R1
    invitee = user_factory()  # will be invited to R2
    other = user_factory()  # creates R2

    api_client.force_authenticate(owner)

    # R1: created by owner
    api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "R1",
            "content": "x",
            "requestee_emails": [invitee.email],
        },
        format="json",
    )

    # R2: created by 'other', owner is invited
    api_client.force_authenticate(other)
    api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "R2",
            "content": "y",
            "requestee_emails": [owner.email],
        },
        format="json",
    )

    # Assertions
    api_client.force_authenticate(owner)

    owned_resp = api_client.get(
        reverse("api:feedback-requests-list"), {"type": "owned"}
    )
    invited_resp = api_client.get(
        reverse("api:feedback-requests-list"), {"type": "invited"}
    )

    assert owned_resp.status_code == 200
    assert invited_resp.status_code == 200

    owned_titles = {r["title"] for r in owned_resp.data}
    invited_titles = {r["title"] for r in invited_resp.data}

    assert owned_titles == {"R1"}
    assert invited_titles == {"R2"}
    assert owned_titles.isdisjoint(invited_titles)


@pytest.mark.django_db
def test_unrelated_user_gets_empty_lists(api_client, user_factory):
    """
    A user who is neither owner nor invitee of any request should see
    empty results from both filters.
    """
    someone = user_factory()
    other = user_factory()

    # 'other' creates a request unrelated to 'someone'
    api_client.force_authenticate(other)
    api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Unrelated",
            "content": "x",
            "requestee_emails": [],
        },
        format="json",
    )

    api_client.force_authenticate(someone)
    assert (
        api_client.get(reverse("api:feedback-requests-list"), {"type": "owned"}).data
        == []
    )
    assert (
        api_client.get(reverse("api:feedback-requests-list"), {"type": "invited"}).data
        == []
    )


@pytest.mark.django_db
def test_all_filter_returns_both_owned_and_invited(api_client, user_factory):
    """
    The "type=all" filter (or no filter) must return both owned and invited requests.
    """
    owner = user_factory()  # will own R1
    invitee = user_factory()  # will be invited to R2
    other = user_factory()  # creates R2

    api_client.force_authenticate(owner)

    # R1: created by owner
    api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "R1",
            "content": "x",
            "requestee_emails": [invitee.email],
        },
        format="json",
    )

    # R2: created by 'other', owner is invited
    api_client.force_authenticate(other)
    api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "R2",
            "content": "y",
            "requestee_emails": [owner.email],
        },
        format="json",
    )

    # Assertions
    api_client.force_authenticate(owner)

    all_resp = api_client.get(reverse("api:feedback-requests-list"), {"type": "all"})
    default_resp = api_client.get(reverse("api:feedback-requests-list"))

    assert all_resp.status_code == 200
    assert default_resp.status_code == 200

    all_titles = {r["title"] for r in all_resp.data}
    default_titles = {r["title"] for r in default_resp.data}

    assert all_titles == {"R1", "R2"}
    assert default_titles == {"R1", "R2"}


@pytest.mark.django_db
def test_setting_mentioned_users_on_feedback_creation(api_client, user, receiver, mentioned_user):
    """Mentioned users included in payload should be linked to the feedback note."""
    api_client.force_authenticate(user)
    payload = {
        "receiver_ids": [str(receiver.uuid)],
        "content": "Testing mentions",
        "mentioned_users": [mentioned_user.email]
    }
    url = reverse("api:feedback-entries-list")
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED

    fb_uuid = resp.data["uuid"]
    fb = Feedback.objects.get(uuid=fb_uuid)
    assert list(fb.note.mentioned_users.all()) == [mentioned_user]


@pytest.mark.django_db
def test_bulk_feedback_creation(api_client, user, receiver, outsider):
    """User can send the same ad-hoc feedback to multiple recipients at once."""
    api_client.force_authenticate(user)

    url = reverse("api:feedback-entries-list")
    payload = {
        "receiver_ids": [str(receiver.uuid), str(outsider.uuid)],
        "content": "Great teamwork!",
        "evidence": "PR #456"
    }

    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED

    # Should get back a list of two feedback objects
    assert isinstance(resp.data, list)
    assert len(resp.data) == 2

    returned_uuids = {item["uuid"] for item in resp.data}
    feedbacks = Feedback.objects.filter(uuid__in=returned_uuids)
    assert feedbacks.count() == 2

    # Verify each feedback entry
    for fb in feedbacks:
        assert fb.sender == user
        assert fb.content == "Great teamwork!"
        assert fb.evidence == "PR #456"
        assert str(fb.receiver.uuid) in payload["receiver_ids"]


# ──────────────────────────────────────────────────
# ACL Tests: Security fix for feedback privacy
# ──────────────────────────────────────────────────


@pytest.mark.django_db
def test_sender_leader_cannot_access_feedback(api_client, user_factory):
    """CRITICAL: Sender's leader must NOT have access to feedback sent by their team member."""
    leader = user_factory()
    sender = user_factory(leader=leader)
    receiver = user_factory()

    # Sender sends feedback to receiver
    api_client.force_authenticate(sender)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "Great work on the project!",
        },
        format="json",
    ).data["uuid"]

    # Leader should NOT be able to view the feedback
    api_client.force_authenticate(leader)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    # Verify NoteUserAccess: leader should not have a record or it should be can_view=False
    fb = Feedback.objects.get(uuid=fb_uuid)
    leader_access = NoteUserAccess.objects.filter(user=leader, note=fb.note).first()
    if leader_access:
        assert leader_access.can_view is False


@pytest.mark.django_db
def test_sender_agile_coach_cannot_access_feedback(api_client, user_factory):
    """CRITICAL: Sender's agile coach must NOT have access to feedback sent by their coachee."""
    agile_coach = user_factory()
    sender = user_factory(agile_coach=agile_coach)
    receiver = user_factory()

    # Sender sends feedback to receiver
    api_client.force_authenticate(sender)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "Excellent presentation!",
        },
        format="json",
    ).data["uuid"]

    # Agile coach should NOT be able to view the feedback
    api_client.force_authenticate(agile_coach)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    # Verify NoteUserAccess: agile coach should not have a record or it should be can_view=False
    fb = Feedback.objects.get(uuid=fb_uuid)
    coach_access = NoteUserAccess.objects.filter(user=agile_coach, note=fb.note).first()
    if coach_access:
        assert coach_access.can_view is False


@pytest.mark.django_db
def test_feedback_acl_only_sender_receiver_mentioned(api_client, user, receiver, mentioned_user):
    """Verify NoteUserAccess records are created ONLY for sender, receiver, and mentioned users."""
    api_client.force_authenticate(user)
    payload = {
        "receiver_ids": [str(receiver.uuid)],
        "content": "Great collaboration!",
        "mentioned_users": [mentioned_user.email],
    }
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"), payload, format="json"
    ).data["uuid"]

    fb = Feedback.objects.get(uuid=fb_uuid)
    
    # Check that exactly 3 users have access
    access_records = NoteUserAccess.objects.filter(note=fb.note, can_view=True)
    assert access_records.count() == 3

    # Verify each expected user has access
    sender_access = NoteUserAccess.objects.get(user=user, note=fb.note)
    assert sender_access.can_view is True
    assert sender_access.can_edit is True

    receiver_access = NoteUserAccess.objects.get(user=receiver, note=fb.note)
    assert receiver_access.can_view is True
    assert receiver_access.can_edit is False

    mentioned_access = NoteUserAccess.objects.get(user=mentioned_user, note=fb.note)
    assert mentioned_access.can_view is True
    assert mentioned_access.can_edit is False


@pytest.mark.django_db
def test_feedback_request_acl_owner_requestees_mentioned(
    api_client, user, receiver, mentioned_user
):
    """Verify FeedbackRequest notes grant access to owner, requestees, and mentioned users."""
    api_client.force_authenticate(user)
    payload = {
        "title": "Need feedback on my proposal",
        "content": "Please review my work",
        "requestee_emails": [receiver.email],
        "mentioned_users": [mentioned_user.email],
    }
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"), payload, format="json"
    ).data["uuid"]

    fr = FeedbackRequest.objects.get(uuid=fr_uuid)
    
    # Check that exactly 3 users have access
    access_records = NoteUserAccess.objects.filter(note=fr.note, can_view=True)
    assert access_records.count() == 3

    # Verify each expected user has access
    owner_access = NoteUserAccess.objects.get(user=user, note=fr.note)
    assert owner_access.can_view is True
    assert owner_access.can_edit is True

    requestee_access = NoteUserAccess.objects.get(user=receiver, note=fr.note)
    assert requestee_access.can_view is True
    assert requestee_access.can_edit is False

    mentioned_access = NoteUserAccess.objects.get(user=mentioned_user, note=fr.note)
    assert mentioned_access.can_view is True
    assert mentioned_access.can_edit is False


@pytest.mark.django_db
def test_feedback_request_owner_leader_cannot_access(api_client, user_factory):
    """CRITICAL: Request owner's leader must NOT have automatic access to the request."""
    leader = user_factory()
    owner = user_factory(leader=leader)
    requestee = user_factory()

    # Owner creates feedback request
    api_client.force_authenticate(owner)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need feedback",
            "content": "Please review my work",
            "requestee_emails": [requestee.email],
        },
        format="json",
    ).data["uuid"]

    # Leader should NOT be able to view the request
    api_client.force_authenticate(leader)
    resp = api_client.get(
        reverse("api:feedback-requests-detail", kwargs={"uuid": fr_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    # Verify NoteUserAccess
    fr = FeedbackRequest.objects.get(uuid=fr_uuid)
    leader_access = NoteUserAccess.objects.filter(user=leader, note=fr.note).first()
    if leader_access:
        assert leader_access.can_view is False


@pytest.mark.django_db
def test_mentioned_user_in_feedback_request_gets_access(
    api_client, user, receiver, mentioned_user
):
    """Mentioned users in feedback requests should have proper access."""
    api_client.force_authenticate(user)
    payload = {
        "title": "Need feedback",
        "content": f"cc @{mentioned_user.email}",
        "requestee_emails": [receiver.email],
        "mentioned_users": [mentioned_user.email],
    }
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"), payload, format="json"
    ).data["uuid"]

    # Mentioned user should be able to view the request
    api_client.force_authenticate(mentioned_user)
    resp = api_client.get(
        reverse("api:feedback-requests-detail", kwargs={"uuid": fr_uuid})
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify ACL
    fr = FeedbackRequest.objects.get(uuid=fr_uuid)
    mentioned_access = NoteUserAccess.objects.get(user=mentioned_user, note=fr.note)
    assert mentioned_access.can_view is True


@pytest.mark.django_db
def test_mentioned_in_request_sees_all_answers(
    api_client, user_factory, mentioned_user
):
    """
    Users mentioned in the ORIGINAL REQUEST should see ALL answers submitted to that request.
    This implements transparency for stakeholders mentioned in the request.
    """
    user = user_factory()  # Request owner
    receiver1 = user_factory()  # First requestee
    receiver2 = user_factory()  # Second requestee

    # Step 1: User creates request and mentions mentioned_user in the REQUEST
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need feedback on my project",
            "content": f"Please review my work. cc @{mentioned_user.email}",
            "requestee_emails": [receiver1.email, receiver2.email],
            "mentioned_users": [mentioned_user.email],  # KEY: Mentioned in REQUEST
        },
        format="json",
    ).data["uuid"]

    # Step 2: First requestee answers (does NOT mention mentioned_user in answer)
    api_client.force_authenticate(receiver1)
    fb1_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "Great work on the backend!",
        },
        format="json",
    ).data["uuid"]

    # Step 3: Second requestee answers (also does NOT mention mentioned_user)
    api_client.force_authenticate(receiver2)
    fb2_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "Frontend needs improvement.",
        },
        format="json",
    ).data["uuid"]

    # Step 4: mentioned_user should see BOTH answers (because they were mentioned in REQUEST)
    api_client.force_authenticate(mentioned_user)
    resp1 = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb1_uuid})
    )
    resp2 = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid})
    )
    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK

    # Verify ACL: mentioned_user has access to both answers
    fb1 = Feedback.objects.get(uuid=fb1_uuid)
    fb2 = Feedback.objects.get(uuid=fb2_uuid)
    
    mentioned_access1 = NoteUserAccess.objects.get(user=mentioned_user, note=fb1.note)
    assert mentioned_access1.can_view is True
    
    mentioned_access2 = NoteUserAccess.objects.get(user=mentioned_user, note=fb2.note)
    assert mentioned_access2.can_view is True

    # Step 5: Verify receiver1 CANNOT see receiver2's answer (privacy maintained)
    api_client.force_authenticate(receiver1)
    resp = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid})
    )
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
def test_feedback_note_type_excluded_from_generic_signal(api_client, user_factory):
    """
    Regression test: Verify that FEEDBACK notes bypass the generic signal handler
    and don't get automatic leader/coach access grants.
    """
    leader = user_factory()
    agile_coach = user_factory()
    sender = user_factory(leader=leader, agile_coach=agile_coach)
    receiver = user_factory()

    # Create feedback
    api_client.force_authenticate(sender)
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(receiver.uuid)],
            "content": "Excellent work!",
        },
        format="json",
    ).data["uuid"]

    fb = Feedback.objects.get(uuid=fb_uuid)
    
    # Verify the note type is FEEDBACK
    assert fb.note.type == NoteType.FEEDBACK

    # Verify leader and agile coach do NOT have access records (or have can_view=False)
    leader_access = NoteUserAccess.objects.filter(
        user=leader, note=fb.note, can_view=True
    ).first()
    assert leader_access is None

    coach_access = NoteUserAccess.objects.filter(
        user=agile_coach, note=fb.note, can_view=True
    ).first()
    assert coach_access is None


@pytest.mark.django_db
def test_service_layer_grant_feedback_access_function(user_factory, _current_cycle):
    """Direct unit test for grant_feedback_access service function."""
    from api.services import grant_feedback_access

    sender = user_factory()
    receiver = user_factory()
    mentioned_user = user_factory()

    # Create a feedback note manually
    note = Note.objects.create(
        owner=sender,
        title="Test Feedback",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.FEEDBACK,
        cycle=_current_cycle,
    )
    note.mentioned_users.set([mentioned_user])

    # Call the service function
    grant_feedback_access(note, receiver, [mentioned_user])

    # Verify access records
    sender_access = NoteUserAccess.objects.get(user=sender, note=note)
    assert sender_access.can_view is True
    assert sender_access.can_edit is True

    receiver_access = NoteUserAccess.objects.get(user=receiver, note=note)
    assert receiver_access.can_view is True
    assert receiver_access.can_edit is False

    mentioned_access = NoteUserAccess.objects.get(user=mentioned_user, note=note)
    assert mentioned_access.can_view is True
    assert mentioned_access.can_edit is False


@pytest.mark.django_db
def test_service_layer_grant_feedback_request_access_function(user_factory, _current_cycle):
    """Direct unit test for grant_feedback_request_access service function."""
    from api.services import grant_feedback_request_access

    owner = user_factory()
    requestee1 = user_factory()
    requestee2 = user_factory()
    mentioned_user = user_factory()

    # Create a feedback request note manually
    note = Note.objects.create(
        owner=owner,
        title="Test Request",
        content="Test content",
        date=timezone.now().date(),
        type=NoteType.FEEDBACK_REQUEST,
        cycle=_current_cycle,
    )
    note.mentioned_users.set([mentioned_user])

    # Call the service function
    grant_feedback_request_access(note, [requestee1, requestee2], [mentioned_user])

    # Verify access records
    owner_access = NoteUserAccess.objects.get(user=owner, note=note)
    assert owner_access.can_view is True
    assert owner_access.can_edit is True

    req1_access = NoteUserAccess.objects.get(user=requestee1, note=note)
    assert req1_access.can_view is True
    assert req1_access.can_edit is False

    req2_access = NoteUserAccess.objects.get(user=requestee2, note=note)
    assert req2_access.can_view is True
    assert req2_access.can_edit is False

    mentioned_access = NoteUserAccess.objects.get(user=mentioned_user, note=note)
    assert mentioned_access.can_view is True
    assert mentioned_access.can_edit is False


@pytest.mark.django_db
def test_retrieve_mentions_excludes_observer_feedback_answers(
    api_client, user_factory, mentioned_user
):
    """
    Test that /api/notes/?retrieve_mentions=true excludes feedback answers where
    the user is only mentioned in the parent REQUEST (observer role), preventing
    phantom notification badges.
    
    Scenario:
    - User A creates request, mentions User C
    - User B submits answer
    - User C should see REQUEST in retrieve_mentions (✓ notification)
    - User C should NOT see ANSWER in retrieve_mentions (✗ no phantom badge)
    - User C can still ACCESS the answer via detail endpoint (✓ security maintained)
    """
    user_a = user_factory()  # Request owner
    user_b = user_factory()  # Requestee
    user_c = mentioned_user  # Mentioned in REQUEST
    
    # Step 1: User A creates request and mentions User C
    api_client.force_authenticate(user_a)
    fr_response = api_client.post(
        reverse("api:feedback-requests-list"),
        {
            "title": "Need feedback on project",
            "content": f"Please review. cc @{user_c.email}",
            "requestee_emails": [user_b.email],
            "mentioned_users": [user_c.email],
        },
        format="json",
    )
    assert fr_response.status_code == status.HTTP_201_CREATED
    fr_uuid = fr_response.data["uuid"]
    fr_note_uuid = fr_response.data["note"]["uuid"]
    
    # Step 2: User B submits answer
    api_client.force_authenticate(user_b)
    fb_response = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_ids": [str(user_a.uuid)],
            "feedback_request_uuid": str(fr_uuid),
            "content": "Great work on the backend!",
        },
        format="json",
    )
    assert fb_response.status_code == status.HTTP_201_CREATED
    fb_uuid = fb_response.data["uuid"]
    fb_note_uuid = fb_response.data["note"]["uuid"]
    
    # Step 3: Check User C's retrieve_mentions (notifications)
    api_client.force_authenticate(user_c)
    
    # User C SHOULD see the REQUEST in retrieve_mentions
    mentions_response = api_client.get(
        reverse("api:note-list"),
        {"retrieve_mentions": "true"}
    )
    assert mentions_response.status_code == status.HTTP_200_OK
    mention_note_uuids = [note["uuid"] for note in mentions_response.data]
    
    assert fr_note_uuid in mention_note_uuids, "User C should see REQUEST in notifications"
    assert fb_note_uuid not in mention_note_uuids, "User C should NOT see ANSWER in notifications (no phantom badge)"
    
    # Step 4: Verify User C can still ACCESS the answer directly (security maintained)
    answer_detail_response = api_client.get(
        reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})
    )
    assert answer_detail_response.status_code == status.HTTP_200_OK, "User C should still have access to read the answer directly"
