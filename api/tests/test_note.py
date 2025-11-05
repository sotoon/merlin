import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Note

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    # adjust create_user args if your User model requires more/less fields
    return User.objects.create_user(
        email="selfmention@example.com",
        password="password123",
        username="selfmention@example.com",
    )


@pytest.mark.django_db
def test_cannot_mention_self(api_client, user):
    api_client.force_authenticate(user=user)
    payload = {
        "title": "Self-mention test",
        "content": "I'm going to mention myself…",
        "date": "2025-07-02",
        "mentioned_users": [user.email],
    }
    resp = api_client.post("/api/notes/", payload, format="json")
    assert resp.status_code == 400
    assert "mentioned_users" in resp.data


@pytest.mark.django_db
def test_create_note_with_linked_notes_returns_detailed_objects(api_client, user):
    api_client.force_authenticate(user=user)

    # Create two candidate notes to link to
    linked_1 = Note.objects.create(
        owner=user,
        title="Linked A",
        content="a",
        date="2025-01-01",
    )
    linked_2 = Note.objects.create(
        owner=user,
        title="Linked B",
        content="b",
        date="2025-01-02",
    )

    # Mark one as read by the user to validate read_status
    linked_2.read_by.add(user)

    resp = api_client.post(
        "/api/notes/",
        {
            "title": "Parent",
            "content": "parent",
            "date": "2025-02-01",
            "linked_notes": [str(linked_1.uuid), str(linked_2.uuid)],
        },
        format="json",
    )
    assert resp.status_code == 201
    assert isinstance(resp.data.get("linked_notes"), list)
    uuids = {ln["uuid"] for ln in resp.data["linked_notes"]}
    assert uuids == {str(linked_1.uuid), str(linked_2.uuid)}

    # Ensure serializer shape and read_status presence
    sample = resp.data["linked_notes"][0]
    assert {
        "uuid",
        "title",
        "type",
        "one_on_one_member",
        "one_on_one_id",
        "feedback_uuid",
        "feedback_request_uuid",
        "feedback_request_uuid_of_feedback",
        "read_status",
    }.issubset(sample.keys())

    # Check read_status matches expectation
    by_uuid = {ln["uuid"]: ln for ln in resp.data["linked_notes"]}
    assert by_uuid[str(linked_1.uuid)]["read_status"] in (False, 0)
    assert by_uuid[str(linked_2.uuid)]["read_status"] in (True, 1, "true", "True")


@pytest.mark.django_db
def test_update_note_can_clear_linked_notes(api_client, user):
    api_client.force_authenticate(user=user)

    # Create parent and a linked note
    parent = Note.objects.create(
        owner=user,
        title="Parent",
        content="p",
        date="2025-03-01",
    )
    ln = Note.objects.create(
        owner=user,
        title="Child",
        content="c",
        date="2025-03-02",
    )
    parent.linked_notes.add(ln)

    # Clear all links
    resp = api_client.patch(
        f"/api/notes/{parent.uuid}/",
        {"linked_notes": []},
        format="json",
    )
    assert resp.status_code in (200, 202)

    parent.refresh_from_db()
    assert parent.linked_notes.count() == 0
