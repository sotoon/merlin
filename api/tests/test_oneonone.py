import pytest
import factory
from pytest_factoryboy import register
from django.utils import timezone
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from api.models import User, Note, OneOnOne, ValueTag, ValueSection, OrgValueTag, Cycle, UserTimeline, NoteUserAccess
from api.services.note_access import grant_oneonone_access, ensure_leader_note_accesses


"""One-on-One Feature Tests
Covering:
• model rules & constraints
• service helpers that grant access
• permission enforcement
• REST endpoints (leader-member flows)
• timeline side-effects
• analytics/tag reports
"""


#   Factory classes
class CycleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cycle

    name = factory.Sequence(lambda n: f"Cycle-{n}")
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date   = factory.LazyFunction(lambda: timezone.now().date())


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@sotoon.ir")
    password = factory.PostGenerationMethodCall("set_password", "pw")
    name = factory.Faker("name")


class ValueTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ValueTag

    name_en = factory.Sequence(lambda n: f"Tag{n}")
    name_fa = "تگ"
    section = ValueSection.PERSONAL


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    owner = factory.SubFactory(UserFactory)
    title = "1×1 auto note"
    type = "OneOnOne"
    cycle = factory.SubFactory(CycleFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())


class OneOnOneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OneOnOne

    note = factory.SubFactory(NoteFactory)
    member = factory.SubFactory(UserFactory)
    cycle = factory.SelfAttribute("note.cycle")
    performance_summary = "Initial perf."

    @factory.post_generation
    def _ensure_leader(obj, create, extracted, **kwargs):
        if not create:
            return
        leader = obj.note.owner
        if obj.member_id == leader.id:
            # If they coincided, create a fresh leader
            leader = UserFactory()
            obj.note.owner = leader
            obj.note.save(update_fields=["owner"])
        # Now set the leader relationship
        obj.member.leader = leader
        obj.member.save(update_fields=["leader"])
        # Seed ACLs
        from api.services.note_access import grant_oneonone_access
        grant_oneonone_access(obj.note)

# register fixtures
register(UserFactory)
register(CycleFactory)
register(UserFactory, "leader")
register(UserFactory, "member")
register(UserFactory, "outsider")
register(ValueTagFactory, "personal_tag")
register(NoteFactory)
register(OneOnOneFactory)


# DRF API client fixture
@pytest.fixture
def api_client():
    return APIClient()


# 1  Model constraints

@pytest.mark.django_db
def test_oneonone_requires_note_and_member(cycle):
    """Creating OneOnOne without FK note/member must fail."""
    with pytest.raises(Exception):
        OneOnOne.objects.create(cycle=cycle, performance_summary="x")


@pytest.mark.django_db
def test_summary_length_limit(note, member):
    """Performance summary >400 chars rejected."""
    too_long = "x" * 401
    with pytest.raises(Exception):
        OneOnOne.objects.create(note=note, member=member, cycle=note.cycle, performance_summary=too_long)


# 2  Access‑seeding helpers

@pytest.mark.django_db
def test_grant_oneonone_access_creates_records(one_on_one):
    """grant_oneonone_access seeds NoteUserAccess rows for leader and member."""
    note   = one_on_one.note
    leader = note.owner
    member = one_on_one.member

    grant_oneonone_access(note)
    assert NoteUserAccess.objects.filter(user=leader, note=note, can_view=True).exists()
    assert NoteUserAccess.objects.filter(user=member, note=note, can_view=True).exists()


@pytest.mark.django_db
def test_leader_not_added_to_one_on_one(leader, member, note_factory):
    note = note_factory(owner=member, type="OneOnOne")
    ensure_leader_note_accesses(member, leader)
    assert not NoteUserAccess.objects.filter(user=leader, note=note).exists()


# 3  Tag‑section business rules

@pytest.mark.django_db
def test_only_enabled_tags_attach(personal_tag, note_factory, user_factory):
    OrgValueTag.objects.create(tag=personal_tag, is_enabled=True)
    note   = NoteFactory()
    member = UserFactory()
    obj = OneOnOne.objects.create(note=note, member=member, cycle=note.cycle, performance_summary="ok")
    obj.tags.add(personal_tag)  # allowed

    bad_tag = ValueTagFactory(section=ValueSection.PERSONAL)
    OrgValueTag.objects.create(tag=bad_tag, is_enabled=False)
    with pytest.raises(Exception):
        obj.tags.add(bad_tag)


# 4  Permission enforcement

@pytest.mark.django_db
def test_has_oneonone_access(api_client, outsider, one_on_one):
    leader = one_on_one.note.owner
    member = one_on_one.member

    url = reverse("api:member-oneonones-detail", kwargs={
        "member_pk": str(member.uuid),
        "pk": one_on_one.pk})

    api_client.force_authenticate(leader)
    assert api_client.get(url).status_code == status.HTTP_200_OK

    api_client.force_authenticate(member)
    assert api_client.get(url).status_code == status.HTTP_200_OK

    api_client.force_authenticate(outsider)
    assert api_client.get(url).status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


# 5  Endpoint flows

@pytest.mark.django_db
def test_leader_can_create_one_on_one(api_client, one_on_one, cycle):
    leader = one_on_one.note.owner
    member = one_on_one.member

    url = reverse("api:member-oneonones-list", kwargs={
        "member_pk": str(member.uuid)})
    api_client.force_authenticate(leader)
    data = {
        "cycle": cycle.pk,
        "performance_summary": "Great",
        "actions": "Lurem ipsum",
        "leader_vibe": ":)",
        "member_vibe": ":(",
        "tags": [],
    }
    resp = api_client.post(url, data, format="json")
    print(resp.status_code, resp.data)
    assert resp.status_code == status.HTTP_201_CREATED

    note_uuid = resp.data["note_meta"]["id"]
    assert NoteUserAccess.objects.filter(
        note__pk=note_uuid, user=leader, can_edit=True
    ).exists()


@pytest.mark.django_db
def test_only_current_cycle_editable(api_client, one_on_one):
    # Make sure the one_on_one is in the current cycle
    leader = one_on_one.note.owner
    current_cycle = Cycle.get_current_cycle()
    one_on_one.cycle = current_cycle
    one_on_one.save()

    url = reverse("api:member-oneonones-detail", kwargs={
        "member_pk": str(one_on_one.member.uuid),
        "pk": one_on_one.pk
    })
    api_client.force_authenticate(leader)

    # Should be editable in current cycle
    resp = api_client.patch(url, {"performance_summary": "Edited!"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    one_on_one.refresh_from_db()
    assert one_on_one.performance_summary == "Edited!"

    # Move to a previous (fake) cycle
    past_cycle = Cycle.objects.create(name="Past", start_date="2000-01-01", end_date="2000-12-31")
    one_on_one.cycle = past_cycle
    one_on_one.save()

    # Should be forbidden to edit now
    resp = api_client.patch(url, {"performance_summary": "Still edited?"}, format="json")
    print (resp)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    # Make sure value didn't change
    one_on_one.refresh_from_db()
    assert one_on_one.performance_summary == "Edited!"


@pytest.mark.django_db
def test_member_cannot_create(api_client, one_on_one, cycle):
    member = one_on_one.member
    url = reverse("api:member-oneonones-list", kwargs=
                  {"member_pk": str(member.uuid)})
    api_client.force_authenticate(member)
    data = {
        "cycle": cycle.pk,
        "performance_summary": "Test summary",
        "actions": "Something here",
        "leader_vibe": ":)",
        "member_vibe": ":(",
        "tags": [],
    }
    resp = api_client.post(url, data, format="json")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_member_can_only_patch_member_vibe(api_client, one_on_one):
    member = one_on_one.member
    url = reverse("api:member-oneonones-detail", kwargs={
        "member_pk": str(member.uuid),
        "pk": one_on_one.pk,
    })
    api_client.force_authenticate(member)

    # Allowed: member can patch their vibe
    resp = api_client.patch(url, {"member_vibe": ":)"}, format="json")
    assert resp.status_code == status.HTTP_200_OK

    # Not allowed: member tries to patch another field
    resp = api_client.patch(url, {"performance_summary": "Hacked!"}, format="json")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Not allowed: member tries to patch both vibe and other fields
    resp = api_client.patch(url, {"member_vibe": ":D", "performance_summary": "foo"}, format="json")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_oneonone_acl_member_leader_persistence(
    user_factory, cycle_factory, note_factory, one_on_one_factory
):
    """
    Member should see all their 1:1s, even after leader changes.
    Each leader sees only their 1:1s with a member.
    Outsiders never get access.
    """
    cycle = cycle_factory()
    # Create initial leader and member
    leader1 = user_factory()
    leader2 = user_factory()
    member = user_factory(leader=leader1)
    outsider = user_factory()

    # 1. First 1-on-1 (with leader1)
    note1 = note_factory(owner=leader1, type="OneOnOne", cycle=cycle)
    ooo1 = one_on_one_factory(note=note1, member=member, cycle=cycle)
    grant_oneonone_access(note1)

    # Member should have access to note1
    assert NoteUserAccess.objects.filter(user=member, note=note1, can_view=True).exists()
    # Leader1 should have access to note1
    assert NoteUserAccess.objects.filter(user=leader1, note=note1, can_view=True).exists()

    # 2. Change member's leader
    member.leader = leader2
    member.save()

    # 3. Second 1-on-1 (with leader2)
    note2 = note_factory(owner=leader2, type="OneOnOne", cycle=cycle)
    ooo2 = one_on_one_factory(note=note2, member=member, cycle=cycle)
    grant_oneonone_access(note2)

    # Member should have access to BOTH notes
    member_note_uuids = set(
        Note.objects.filter(noteuseraccess__user=member, type="OneOnOne")
        .values_list("uuid", flat=True)
    )
    assert member_note_uuids == {note1.uuid, note2.uuid}

    # Leader1 only sees their 1:1
    leader1_note_uuids = set(
        Note.objects.filter(noteuseraccess__user=leader1, type="OneOnOne")
        .values_list("uuid", flat=True)
    )
    assert leader1_note_uuids == {note1.uuid}
    # Leader2 only sees their 1:1
    leader2_note_uuids = set(
        Note.objects.filter(noteuseraccess__user=leader2, type="OneOnOne")
        .values_list("uuid", flat=True)
    )
    assert leader2_note_uuids == {note2.uuid}

    # Member can view details (permission)
    assert NoteUserAccess.objects.get(note=note1, user=member).can_view
    assert NoteUserAccess.objects.get(note=note2, user=member).can_view
    # Leaders can edit their own 1:1s
    assert NoteUserAccess.objects.get(note=note1, user=leader1).can_edit
    assert NoteUserAccess.objects.get(note=note2, user=leader2).can_edit

    # Outsider gets NO access
    assert not NoteUserAccess.objects.filter(user=outsider, note=note1).exists()
    assert not NoteUserAccess.objects.filter(user=outsider, note=note2).exists()

    # Now, if member leaves leader2, access remains unless explicitly cleaned up
    member.leader = None
    member.save()
    # Member still has access to both
    member_note_uuids_after = set(
        Note.objects.filter(noteuseraccess__user=member, type="OneOnOne")
        .values_list("uuid", flat=True)
    )
    assert member_note_uuids_after == {note1.uuid, note2.uuid}
    # Leader2 still only has their own, unless cleanup logic is added
    leader2_note_uuids_after = set(
        Note.objects.filter(noteuseraccess__user=leader2, type="OneOnOne")
        .values_list("uuid", flat=True)
    )
    assert leader2_note_uuids_after == {note2.uuid}


@pytest.mark.django_db
def test_member_can_list_and_view(api_client, one_on_one_factory, user_factory):
    leader = user_factory()
    member = user_factory(leader=leader)
    ooo1 = one_on_one_factory(note__owner=leader, member=member)
    ooo2 = one_on_one_factory(note__owner=leader, member=member)

    list_url = reverse("api:my-one-on-ones-list")

    api_client.force_authenticate(member)
    resp = api_client.get(list_url)
    assert resp.status_code == 200
    assert {ooo1.id, ooo2.id} == {obj["id"] for obj in resp.data}

    detail_url = reverse("api:my-one-on-ones-detail",
                         kwargs={"pk": ooo1.pk})
    assert api_client.get(detail_url).status_code == 200


@pytest.mark.django_db
def test_vibe_privacy(api_client, member, one_on_one):
    leader = one_on_one.note.owner
    url = reverse("api:member-oneonones-detail", kwargs={"member_pk": str(member.uuid), "pk": one_on_one.pk})
    api_client.force_authenticate(member)
    api_client.patch(url, {"member_vibe": ":)"}, format="json")
    api_client.force_authenticate(leader)
    assert api_client.get(url).data.get("member_vibe") is None


@pytest.mark.django_db
def test_my_team_lists_reports(api_client, leader, member, outsider):
    member.leader = leader
    member.save()    

    url = reverse("api:my-team-list")
    api_client.force_authenticate(leader)

    ids = {item["uuid"] for item in api_client.get(url).data}

    assert str(member.uuid)   in ids
    assert str(outsider.uuid) not in ids


# 6  Timeline logging


# 8  Analytics endpoint
