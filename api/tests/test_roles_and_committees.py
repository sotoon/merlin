import pytest
import factory
from pytest_factoryboy import register
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

from api.models import (
    User, Organization, Department, Team, Tribe, Committee,
    Role, RoleType, RoleScope,
    Note, NoteType, NoteSubmitStatus,
    NoteUserAccess,
    Summary, SummarySubmitStatus,
    leader_permissions, committee_roles_permissions,
    Cycle,
)
from api.services.note_access import ensure_leader_note_accesses

# ───────────────────────────────────────────────
# Factory classes
# ───────────────────────────────────────────────

class CycleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cycle

    name = factory.Sequence(lambda n: f"Cycle-{n}")
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date = factory.LazyFunction(lambda: timezone.now().date())
    is_active = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "pw")
    name = factory.Faker("name")


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Dept{n}")


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Org{n}")


class TribeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tribe

    name = factory.Sequence(lambda n: f"Tribe{n}")
    department = factory.SubFactory(DepartmentFactory)


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Team{n}")
    department = factory.SubFactory(DepartmentFactory)
    tribe = factory.SubFactory(TribeFactory)


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    role_type = RoleType.LEADER
    role_scope = RoleScope.USER


class CommitteeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Committee

    name = factory.Sequence(lambda n: f"Committee{n}")

    @factory.post_generation
    def roles(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                obj.roles.add(role)

    @factory.post_generation
    def members(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for member in extracted:
                obj.members.add(member)


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    owner = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Proposal {n}")
    type = NoteType.Proposal
    date = factory.LazyFunction(lambda: timezone.now().date())
    cycle = factory.SubFactory(CycleFactory)
    submit_status = NoteSubmitStatus.INITIAL_SUBMIT


# Register fixtures for easier injection
register(UserFactory)
register(UserFactory, "leader")
register(UserFactory, "mentioned_user")
register(UserFactory, "committee_user")
register(CycleFactory)
register(DepartmentFactory)
register(OrganizationFactory)
register(TeamFactory)
register(TribeFactory)
register(RoleFactory)
register(CommitteeFactory)
register(NoteFactory)


@pytest.fixture(autouse=True)
def _current_cycle(cycle_factory):
    """Ensure an active cycle exists globally for tests that rely on Cycle.default querysets."""
    return cycle_factory()

# ───────────────────────────────────────────────
# Helper util
# ───────────────────────────────────────────────


def _make_user_hierarchy(user, leader=None, team_leader=None, product_director=None, cto=None):
    """Attach leader/team/tribe/org links so role-resolution tests can compose quickly."""
    if leader:
        user.leader = leader
        user.save(update_fields=["leader"])
    if team_leader:
        team = TeamFactory(leader=team_leader)
        user.team = team
        user.save(update_fields=["team"])
    if product_director:
        tribe = TribeFactory(product_director=product_director)
        team = TeamFactory(tribe=tribe)
        user.team = team
        user.save(update_fields=["team"])
    if cto:
        org = OrganizationFactory(cto=cto)
        user.organization = org
        user.save(update_fields=["organization"])


# ───────────────────────────────────────────────
# A. Committee-role resolution
# ───────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.parametrize(
    "role_type, role_scope, setup_fn, expected_attr",
    [
        (RoleType.LEADER, RoleScope.USER, lambda u, l: _make_user_hierarchy(u, leader=l), "leader"),
        (RoleType.LEADER, RoleScope.TEAM, lambda u, l: _make_user_hierarchy(u, team_leader=l), "team_leader"),
        (RoleType.PRODUCT_DIRECTOR, RoleScope.TRIBE, lambda u, l: _make_user_hierarchy(u, product_director=l), "product_director"),
        (RoleType.CTO, RoleScope.ORGANIZATION, lambda u, l: _make_user_hierarchy(u, cto=l), "organization.cto"),
    ],
)
def test_get_committee_role_members_simple(user, leader, role_type, role_scope, setup_fn, expected_attr):
    """User.get_committee_role_members returns the concrete person for each (scope,type) role."""
    setup_fn(user, leader)
    role = RoleFactory(role_type=role_type, role_scope=role_scope)
    committee = CommitteeFactory(roles=[role])
    user.committee = committee
    user.save(update_fields=["committee"])

    members = user.get_committee_role_members()
    assert leader in members


@pytest.mark.django_db
def test_get_committee_role_members_duplicates_removed(user, leader):
    """If two roles resolve to the same physical user, set removes duplicates."""
    _make_user_hierarchy(user, leader=leader, team_leader=leader)
    role1 = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    role2 = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.TEAM)
    committee = CommitteeFactory(roles=[role1, role2])
    user.committee = committee
    user.save(update_fields=["committee"])

    members = user.get_committee_role_members()
    assert len(members) == 1 and leader in members


@pytest.mark.django_db
def test_get_committee_role_members_missing_link_logs_warning(caplog, user):
    """Unresolvable role logs a WARNING and is skipped."""
    caplog.set_level("WARNING")
    role = RoleFactory(role_type=RoleType.CTO, role_scope=RoleScope.ORGANIZATION)
    committee = CommitteeFactory(roles=[role])
    user.committee = committee
    user.save(update_fields=["committee"])

    members = user.get_committee_role_members()
    assert len(members) == 0
    assert any("Unresolved committee role" in rec.message for rec in caplog.records)

# ───────────────────────────────────────────────
# B. Committee.clean validation
# ───────────────────────────────────────────────

@pytest.mark.django_db
def test_committee_clean_valid(user, leader):
    """Committee.full_clean passes when every role can resolve for at least one member."""
    _make_user_hierarchy(user, leader=leader)
    role = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role], members=[user])
    committee.full_clean()  # must not raise


@pytest.mark.django_db
def test_committee_clean_invalid(user):
    """Committee with unresolvable role raises ValidationError."""
    role = RoleFactory(role_type=RoleType.PRODUCT_DIRECTOR, role_scope=RoleScope.TRIBE)
    committee = CommitteeFactory(roles=[role], members=[user])
    with pytest.raises(ValidationError):
        committee.full_clean()

# ───────────────────────────────────────────────
# C. NoteUserAccess permission matrix
# ───────────────────────────────────────────────

@pytest.mark.django_db
def test_draft_proposal_access(user, leader, mentioned_user):
    """Draft Proposal: owner full rights, leader gets leader matrix, mentioned gets view-only, committee not yet granted."""
    _make_user_hierarchy(user, leader=leader)

    # Build committee but do not grant yet
    role = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role], members=[leader])
    user.committee = committee
    user.save(update_fields=["committee"])

    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.INITIAL_SUBMIT)
    note.mentioned_users.add(mentioned_user)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    # Owner
    owner_acl = NoteUserAccess.objects.get(user=user, note=note)
    assert owner_acl.can_view and owner_acl.can_edit

    # Leader
    leader_acl = NoteUserAccess.objects.get(user=leader, note=note)
    expected = leader_permissions[NoteType.Proposal]
    for field, value in expected.items():
        assert getattr(leader_acl, field) == value

    # Mentioned user
    men_acl = NoteUserAccess.objects.get(user=mentioned_user, note=note)
    assert men_acl.can_view and men_acl.can_write_feedback

    # Committee member (leader) already counted but others shouldn't exist yet
    assert NoteUserAccess.objects.filter(user__in=committee.members.all().exclude(pk=leader.pk), note=note).count() == 0


@pytest.mark.django_db
def test_mentioned_overrides_committee_draft(user, mentioned_user):
    """When mentioned user is also a committee member in draft, they still get mentioned-user rights."""
    # Setup committee with mentioned_user as member
    role = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role], members=[mentioned_user])
    user.committee = committee
    user.save(update_fields=["committee"])

    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.INITIAL_SUBMIT)
    note.mentioned_users.add(mentioned_user)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    acl = NoteUserAccess.objects.get(user=mentioned_user, note=note)
    # Should match mentioned-user defaults (view True, edit False, feedback True)
    assert acl.can_view and acl.can_write_feedback and not acl.can_edit


@pytest.mark.django_db
def test_proposal_pending_grants_committee(user, leader, committee_user):
    """When Proposal moves to PENDING, committee role & member users receive committee permission matrix."""
    _make_user_hierarchy(user, leader=leader)
    role = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role], members=[committee_user])
    user.committee = committee
    user.save(update_fields=["committee"])

    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.PENDING)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    # committee_user now has committee rights
    acl = NoteUserAccess.objects.get(user=committee_user, note=note)
    expected = committee_roles_permissions[NoteType.Proposal]
    for field, value in expected.items():
        assert getattr(acl, field) == value


@pytest.mark.django_db
def test_permission_idempotency(user):
    """Running ensure_note_predefined_accesses twice produces no duplicate rows."""
    note = NoteFactory(owner=user)
    NoteUserAccess.ensure_note_predefined_accesses(note)
    first_count = NoteUserAccess.objects.count()
    NoteUserAccess.ensure_note_predefined_accesses(note)
    assert NoteUserAccess.objects.count() == first_count

# ───────────────────────────────────────────────
# D. Signals
# ───────────────────────────────────────────────

@pytest.mark.django_db
def test_post_save_signal_creates_acl(note_factory):
    """Saving a Note triggers post_save signal, creating owner access row."""
    note = note_factory()
    assert NoteUserAccess.objects.filter(user=note.owner, note=note).exists()


@pytest.mark.django_db
def test_committee_members_m2m_signal(user, committee_user):
    """Adding a new member to committee retroactively grants access to existing PENDING proposal."""
    role = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role], members=[user])
    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.PENDING)
    user.committee = committee
    user.save(update_fields=["committee"])

    # initial compute
    NoteUserAccess.ensure_note_predefined_accesses(note)

    # now add new member → signal should grant
    committee.members.add(committee_user)
    assert NoteUserAccess.objects.filter(user=committee_user, note=note).exists()


@pytest.mark.django_db
def test_mentioned_users_m2m_signal(note_factory, user, mentioned_user):
    """Adding a mentioned user via M2M triggers ACL creation."""
    note = note_factory(owner=user)
    note.mentioned_users.add(mentioned_user)
    assert NoteUserAccess.objects.filter(user=mentioned_user, note=note).exists()


@pytest.mark.django_db
def test_summary_done_bumps_note_status(user):
    """When summary submit_status becomes DONE, note.submit_status auto-updates to REVIEWED."""
    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.PENDING)
    summary = Summary.objects.create(note=note, content="sum", submit_status=SummarySubmitStatus.DONE, cycle=note.cycle)
    # post_save on Summary should update note
    note.refresh_from_db()
    assert note.submit_status == NoteSubmitStatus.REVIEWED

# ───────────────────────────────────────────────
# E. Leader change helper
# ───────────────────────────────────────────────

@pytest.mark.django_db
def test_leader_change_updates_acl(user, leader, committee_user):
    """ensure_leader_note_accesses grants new leader access and removes old leader."""
    # old leader
    old_leader = leader
    _make_user_hierarchy(user, leader=old_leader)

    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.PENDING)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    assert NoteUserAccess.objects.filter(user=old_leader, note=note).exists()

    # change leader
    new_leader = committee_user
    user.leader = new_leader
    user.save(update_fields=["leader"])

    ensure_leader_note_accesses(user, new_leader)
    assert NoteUserAccess.objects.filter(user=new_leader, note=note).exists()

# ───────────────────────────────────────────────
# F. Constraints & misc.
# ───────────────────────────────────────────────

@pytest.mark.django_db
def test_note_user_access_uniqueness_constraint(user):
    """Attempting to create duplicate NoteUserAccess row raises IntegrityError."""
    note = NoteFactory(owner=user)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            NoteUserAccess.objects.create(user=user, note=note)


@pytest.mark.django_db
def test_role_unique_together():
    """Duplicate (role_type, role_scope) on Role model not allowed."""
    Role.objects.create(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    with pytest.raises(ValidationError):
        Role.objects.create(role_type=RoleType.LEADER, role_scope=RoleScope.USER)

# ───────────────────────────────────────────────
# New tests: Role validation & Committee.roles signal
# ───────────────────────────────────────────────


@pytest.mark.django_db
def test_role_scope_validation_error():
    """CTO with USER scope should raise ValidationError (attribute missing on User)."""
    with pytest.raises(ValidationError):
        Role.objects.create(role_type=RoleType.CTO, role_scope=RoleScope.USER)


@pytest.mark.django_db
def test_committee_roles_m2m_signal_grants_acl(user, committee_user):
    """Adding a new role to committee triggers ACL creation for existing PENDING proposals."""
    # setup hierarchy so role resolves
    org_cto = committee_user
    org = OrganizationFactory(cto=org_cto)
    user.organization = org
    user.save(update_fields=["organization"])

    role_leader = RoleFactory(role_type=RoleType.LEADER, role_scope=RoleScope.USER)
    committee = CommitteeFactory(roles=[role_leader])
    user.committee = committee
    user.save(update_fields=["committee"])

    note = NoteFactory(owner=user, submit_status=NoteSubmitStatus.PENDING)
    NoteUserAccess.ensure_note_predefined_accesses(note)

    # ensure cto does NOT yet have access
    assert not NoteUserAccess.objects.filter(user=org_cto, note=note).exists()

    # create CTO role (ORG scope) and add to committee → signal should fire
    role_cto = RoleFactory(role_type=RoleType.CTO, role_scope=RoleScope.ORGANIZATION)
    committee.roles.add(role_cto)

    # now acl should exist
    assert NoteUserAccess.objects.filter(user=org_cto, note=note).exists()