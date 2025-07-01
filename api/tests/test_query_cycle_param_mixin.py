"""
Test suite for CycleQueryParamMixin to ensure correct filtering of notes by cycle toggle.
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import Cycle, Note
from api.models.note import NoteType
from api.models.user import User

@pytest.fixture
def user(db):
    """Creates and returns a test user."""
    return User.objects.create_user(username="u1", password="pass")

@pytest.fixture
def cycle_current(db):
    """Creates and returns a Cycle instance that represents the current cycle."""
    return Cycle.objects.create(
        name="Current",
        start_date="2000-01-01",
        end_date="2099-12-31",
    )

@pytest.fixture
def cycle_old(db):
    """Creates and returns a Cycle instance that represents an older cycle."""
    return Cycle.objects.create(
        name="Old",
        start_date="1900-01-01",
        end_date="1999-12-31",
    )

@pytest.fixture(autouse=True)
def patch_current_cycle(monkeypatch, cycle_current):
    """
    Monkey-patches Cycle.get_current_cycle() to always return cycle_current fixture.
    Ensures consistent behavior in tests.
    """
    monkeypatch.setattr(
        Cycle,
        "get_current_cycle",
        classmethod(lambda cls: cycle_current)
    )

@pytest.fixture
def note_factory(db, user):
    """
    Factory fixture to create Note instances with minimal required fields.
    Accepts `cycle` kwarg to assign notes to specific cycles.
    """
    def make(**kwargs):
        defaults = {
            "owner": user,
            "title": "Test Note",
            "content": "x",
            "date": timezone.now().date(),
            "type": NoteType.GOAL,
            "cycle": kwargs.get("cycle"),
        }
        return Note.objects.create(**defaults)
    return make

@pytest.fixture
def client(user):
    """Provides an authenticated API client for the test user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
class TestCycleQueryParamMixin:
    def test_no_param_returns_all(self, client, note_factory, cycle_current, cycle_old):
        """
        When no 'cycle' query parameter is provided, the endpoint should return all notes
        regardless of their cycle assignment.
        """
        n1 = note_factory(cycle=cycle_current)
        n2 = note_factory(cycle=cycle_old)

        url = reverse("api:note-list")
        resp = client.get(url)
        assert resp.status_code == 200

        returned_uuids = {item["uuid"] for item in resp.json()}
        assert str(n1.uuid) in returned_uuids
        assert str(n2.uuid) in returned_uuids

    def test_cycle_true_filters_to_current(self, client, note_factory, cycle_current, cycle_old):
        """
        When 'cycle=true' is provided, the endpoint should return only notes
        in the current cycle.
        """
        n_current = note_factory(cycle=cycle_current)
        _ = note_factory(cycle=cycle_old)

        url = reverse("api:note-list") + "?cycle=true"
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        returned_uuids = {item["uuid"] for item in data}
        assert str(n_current.uuid) in returned_uuids
        assert len(returned_uuids) == 1

    @pytest.mark.parametrize("val", ["false", "0", "no", ""])
    def test_cycle_false_returns_all(self, client, note_factory, cycle_current, cycle_old, val):
        """
        When 'cycle' is set to a falsey value (false, 0, no, or empty),
        the endpoint should return all notes, ignoring cycle filtering.
        """
        n1 = note_factory(cycle=cycle_current)
        n2 = note_factory(cycle=cycle_old)

        url = reverse("api:note-list") + f"?cycle={val}"
        resp = client.get(url)
        assert resp.status_code == 200

        returned_uuids = {item["uuid"] for item in resp.json()}
        assert str(n1.uuid) in returned_uuids
        assert str(n2.uuid) in returned_uuids
