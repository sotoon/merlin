import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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
