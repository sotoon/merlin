import pytest
import uuid
import factory
from pytest_factoryboy import register
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.utils import timezone

from api.models import User, FeedbackForm, Feedback, FeedbackRequest, FeedbackRequestUserLink, Cycle


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
def test_requester_can_create_feedback_request(api_client, user, receiver, feedback_form_factory):
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
    fr_uuid = api_client.post(url, {
        "title": "Need feedback","content":"x","requestee_emails": [receiver.email]}, format="json").data["uuid"]

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
        "receiver_id": str(receiver.uuid),
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

    api_client.force_authenticate(user) # owner/requester
    assert api_client.get(detail_url).status_code == 200


@pytest.mark.django_db
def test_outsider_cannot_access_feedback(api_client, user, receiver, outsider):
    """Outsider must not view someone else's feedback entry."""
    api_client.force_authenticate(user)
    uuid = api_client.post(reverse("api:feedback-entries-list"), {
        "receiver_id": str(receiver.uuid),
        "content": "Hi",
    }, format="json").data["uuid"]

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
    fb1_uuid = api_client.post(reverse("api:feedback-entries-list"), {
        "receiver_id": str(receiver.uuid),
        "content": "fb1",
    }, format="json").data["uuid"]

    # sender2 → receiver
    api_client.force_authenticate(sender2)
    fb2_uuid = api_client.post(reverse("api:feedback-entries-list"), {
        "receiver_id": str(receiver.uuid),
        "content": "fb2",
    }, format="json").data["uuid"]

    # sender1 should NOT see fb2
    api_client.force_authenticate(sender1)
    resp = api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid}))
    assert resp.status_code in (403, 404)

    # sender2 should NOT see fb1
    api_client.force_authenticate(sender2)
    resp = api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb1_uuid}))
    assert resp.status_code in (403, 404)
    
    # receiver can see both
    api_client.force_authenticate(receiver)
    assert api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb1_uuid})).status_code == 200
    assert api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb2_uuid})).status_code == 200


# ──────────────────────────────────────────────────
# Mentioned users access
# ──────────────────────────────────────────────────


@pytest.fixture
def mentioned_user(user_factory):
    """User who will be mentioned in feedback notes."""
    return user_factory()


@pytest.mark.django_db
def test_mentioned_user_can_view_ad_hoc_feedback(api_client, user, receiver, mentioned_user):
    """Mentioned users should gain view access to ad-hoc feedback entries (no request linkage)."""
    # Sender (user) creates ad-hoc feedback for receiver
    api_client.force_authenticate(user)
    fb_uuid = api_client.post(reverse("api:feedback-entries-list"), {
        "receiver_id": str(receiver.uuid),
        "content": "Great collaboration @%s" % mentioned_user.email,
    }, format="json").data["uuid"]

    # Server-side simulation: add mention link (UI would do this)
    fb = Feedback.objects.get(uuid=fb_uuid)
    fb.note.mentioned_users.add(mentioned_user)

    # Mentioned user should be able to read feedback
    api_client.force_authenticate(mentioned_user)
    resp = api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid}))
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_mentioned_user_cannot_view_request_answer(api_client, user, receiver, mentioned_user):
    """Mentioned users must NOT see feedback answers tied to a request (privacy)."""
    # Step 1: user sends request to receiver
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(reverse("api:feedback-requests-list"), {
        "title": "Need feedback",
        "content": "Please give me feedback",
        "requestee_emails": [receiver.email],
    }, format="json").data["uuid"]

    # Step 2: receiver answers the request (creates feedback entry)
    api_client.force_authenticate(receiver)
    fb_uuid = api_client.post(reverse("api:feedback-entries-list"), {
        "receiver_id": str(user.uuid),
        "feedback_request_uuid": str(fr_uuid),
        "content": "Here's my feedback @%s" % mentioned_user.email,
    }, format="json").data["uuid"]

    # Add mention
    fb = Feedback.objects.get(uuid=fb_uuid)
    fb.note.mentioned_users.add(mentioned_user)

    # Mentioned user should be denied access
    api_client.force_authenticate(mentioned_user)
    resp = api_client.get(reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid}))
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
    resp = api_client.post(reverse("api:feedback-requests-list"), payload, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_self_invite_filtered(api_client, user):
    """Owner listed in requestee_emails should not receive a FeedbackRequestUserLink."""
    api_client.force_authenticate(user)
    fr_uuid = api_client.post(
        reverse("api:feedback-requests-list"),
        {"title": "Need feedback", "content": "x", "requestee_emails": [user.email]},
        format="json",
    ).data["uuid"]

    fr = FeedbackRequest.objects.get(uuid=fr_uuid)
    assert not fr.requestees.filter(user=user).exists()


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
    resp = api_client.post(reverse("api:feedback-requests-list"), payload, format="json")
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
            "receiver_id": str(user.uuid),
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
            "receiver_id": str(outsider.uuid),  # wrong receiver
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
        {"receiver_id": str(user.uuid), "content": "to myself"},
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
            "receiver_id": str(user.uuid),
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
            "receiver_id": str(user.uuid),
            "feedback_request_uuid": str(fr_uuid),
            "content": "r1",
        },
        format="json",
    ).data["uuid"]

    api_client.force_authenticate(outsider)
    fb2_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {
            "receiver_id": str(user.uuid),
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
            "receiver_id": str(user.uuid),
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
        {"receiver_id": str(receiver.uuid), "content": "hi"},
        format="json",
    ).data["uuid"]
    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})

    # Sender can PATCH and DELETE
    assert api_client.patch(detail_url, {"content": "edit"}, format="json").status_code == 200
    assert api_client.delete(detail_url).status_code == 204

    # Recreate for negative checks
    fb_uuid = api_client.post(
        reverse("api:feedback-entries-list"),
        {"receiver_id": str(receiver.uuid), "content": "hi2"},
        format="json",
    ).data["uuid"]
    detail_url = reverse("api:feedback-entries-detail", kwargs={"uuid": fb_uuid})

    api_client.force_authenticate(receiver)
    assert api_client.delete(detail_url).status_code in (403, 404)

    api_client.force_authenticate(outsider)
    assert api_client.patch(detail_url, {"content": "x"}, format="json").status_code in (
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
            "receiver_id": str(receiver.uuid),
            "form_uuid": str(inactive_form.uuid),
            "content": "x",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST