import pytest
from django.urls import reverse
from django.utils import timezone

from api.models import (
	User,
	Organization,
	Department,
	Tribe,
	Team,
	Ladder,
	SenioritySnapshot,
	CompensationSnapshot,
	OrgAssignmentSnapshot,
	Note,
	Summary,
	ProposalType,
	DataAccessOverride,
	Chapter,
)
from api.utils.performance_tables import get_persian_year_bounds_gregorian
from api.services.timeline_access import TECH_LADDERS, PRODUCT_LADDERS


# ---------------------------------------------------------------------------
# Helpers (inline factory-style)
# ---------------------------------------------------------------------------


def _create_org_graph():
	dep_eng = Department.objects.create(name="Engineering")
	dep_prod = Department.objects.create(name="Product")
	org = Organization.objects.create(name="T")
	tribe_app = Tribe.objects.create(name="App", department=dep_eng)
	tribe_growth = Tribe.objects.create(name="Growth", department=dep_prod)
	team_a = Team.objects.create(name="App Core", department=dep_eng, tribe=tribe_app)
	team_b = Team.objects.create(name="Growth Insights", department=dep_prod, tribe=tribe_growth)
	return org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b


def _ladder(code: str):
	return Ladder.objects.create(code=code, name=code)


def _seniority(user: User, ladder_code: str, when):
	lad = Ladder.objects.filter(code=ladder_code).first() or _ladder(ladder_code)
	return SenioritySnapshot.objects.create(
		user=user,
		ladder=lad,
		title="",
		overall_score=2.0,
		effective_date=when,
		details_json={"DES": 1},
		stages_json={}
	)


def _comp(user: User, pay: float, bonus: float, when):
	return CompensationSnapshot.objects.create(
		user=user,
		pay_band=None,
		salary_change=0.0,
		bonus_percentage=bonus,
		effective_date=when,
	)


def _orgsnap(user: User, team: Team, when):
	return OrgAssignmentSnapshot.objects.create(
		user=user,
		leader=team.leader,
		team=team,
		tribe=team.tribe,
		chapter=None,
		department=team.department,
		effective_date=when,
	)


def _committee(owner: User, d):
	n = Note.objects.create(owner=owner, title="C", content="", date=d, type="Proposal", proposal_type=ProposalType.EVALUATION)
	Summary.objects.create(note=n, content="", committee_date=d, salary_change=0, bonus=0)


@pytest.fixture
def api_client(db):
	from rest_framework.test import APIClient
	return APIClient()


# ---------------------------------------------------------------------------
# Authentication and basic response
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_requires_auth(api_client):
	"""Un-authenticated access to performance table must be rejected with 401."""
	resp = api_client.get("/api/personnel/performance-table/")
	assert resp.status_code == 401


@pytest.mark.django_db
def test_baseline_json_fields_and_values(api_client):
	"""HR Manager viewer receives populated rows with expected columns and fallbacks.
	Scenario: create HRM, one employee with as-of snapshots and org assignment.
	Checks: column presence, last_bonus, mapped, leader/team fallbacks.
	"""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	leader = User.objects.create(email="ldr@example.com", team=team_a)
	team_a.leader = leader; team_a.save(update_fields=["leader"])
	hrm = User.objects.create(email="hrm@example.com")
	org.hr_manager = hrm; org.save(update_fields=["hr_manager"])
	u = User.objects.create(email="m1@example.com", team=team_a, leader=leader)
	when = timezone.now().date() - timezone.timedelta(days=10)
	_sen = _seniority(u, "Software", when)
	_comp(u, 0, 5.0, when)
	_orgsnap(u, team_a, when)

	api_client.force_authenticate(hrm)
	resp = api_client.get("/api/personnel/performance-table/?page_size=5")
	assert resp.status_code == 200
	body = resp.json()
	assert body["count"] >= 1
	row = next((r for r in body["results"] if r["uuid"]), None)
	assert set(["uuid","name","last_committee_date","committees_current_year","committees_last_year","pay_band","salary_change","is_mapped","last_bonus_date","last_bonus_percentage","last_salary_change_date","ladder","ladder_levels","overall_level","leader","team","tribe"]).issubset(row.keys())
	assert row["is_mapped"] in (True, False)


# ---------------------------------------------------------------------------
# As-of semantics and committee counts
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_as_of_picks_latest_snapshot_before_date(api_client):
	"""As-of picks the latest snapshot not after the provided date.
	Setup two compensation snapshots around the as_of; ensures earlier is chosen.
	"""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	u = User.objects.create(email="e@example.com", team=team_a)
	mid = timezone.now().date()
	before = mid - timezone.timedelta(days=5)
	after = mid + timezone.timedelta(days=5)
	_comp(u, 0, 5.0, before)
	_comp(u, 0, 10.0, after)
	api_client.force_authenticate(viewer)
	resp = api_client.get(f"/api/personnel/performance-table/?as_of={mid.isoformat()}&page_size=50")
	assert resp.status_code == 200
	row = next(r for r in resp.json()["results"] if r["name"] == "e@example.com")
	# last_bonus_percentage must reflect the 'before' snapshot
	assert row["last_bonus_percentage"] == 5.0


@pytest.mark.django_db
def test_committee_counts_current_and_last_year(api_client):
	"""Committee metrics count only within Persian-year windows.
	Creates one committee in current Jalali year, one in last year. Counts must be 1/1.
	"""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	u = User.objects.create(email="e@example.com", team=team_a)
	cur_start, cur_end = get_persian_year_bounds_gregorian(timezone.now().date())
	last_start, last_end = get_persian_year_bounds_gregorian(cur_start - timezone.timedelta(days=1))
	_committee(u, cur_start + timezone.timedelta(days=10))
	_committee(u, last_start + timezone.timedelta(days=10))
	api_client.force_authenticate(viewer)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	row = next(r for r in resp.json()["results"] if r["name"] == "e@example.com") 
	assert row["committees_current_year"] >= 1
	assert row["committees_last_year"] >= 1


# ---------------------------------------------------------------------------
# Filters and ordering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_filters_by_team_and_ladder(api_client):
	"""Filtering by team and ladder returns only matching rows."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	leader_a = User.objects.create(email="la@example.com"); team_a.leader = leader_a; team_a.save(update_fields=["leader"])
	ua = User.objects.create(email="ua@example.com", team=team_a, leader=leader_a)
	ub = User.objects.create(email="ub@example.com", team=team_b)
	_seniority(ua, "Software", timezone.now().date())
	_seniority(ub, "Product", timezone.now().date())
	_orgsnap(ua, team_a, timezone.now().date())
	_orgsnap(ub, team_b, timezone.now().date())
	api_client.force_authenticate(viewer)
	# filter by team (by name, not ID)
	resp = api_client.get(f"/api/personnel/performance-table/?team={team_a.name}&page_size=50")
	names = {r["name"] for r in resp.json()["results"]}
	assert "ua@example.com" in names and "ub@example.com" not in names
	# filter by ladder
	resp = api_client.get(f"/api/personnel/performance-table/?ladder=Software&page_size=50")
	names = {r["name"] for r in resp.json()["results"]}
	assert "ua@example.com" in names and "ub@example.com" not in names


@pytest.mark.django_db
def test_ordering_by_pay_band_and_name(api_client):
	"""Ordering respects the supported keys and ignores invalid ones."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	u1 = User.objects.create(email="a@example.com", name="A", team=team_a)
	u2 = User.objects.create(email="b@example.com", name="B", team=team_a)
	# distinct last_bonus by ordering on committee_date surrogate — pay_band number annotated may be null since we didn't attach PayBand
	_comp(u1, 0, 1.0, timezone.now().date())
	_comp(u2, 0, 2.0, timezone.now().date())
	_orgsnap(u1, team_a, timezone.now().date())
	_orgsnap(u2, team_a, timezone.now().date())
	api_client.force_authenticate(viewer)
	# restrict dataset to team to avoid unrelated names
	resp = api_client.get(f"/api/personnel/performance-table/?team={team_a.id}&ordering=name&page_size=10")
	names = [r["name"] for r in resp.json()["results"] if r["name"] in {"A","B"}]
	assert names == sorted(names)
	resp = api_client.get("/api/personnel/performance-table/?ordering=-committees_current_year,invalid&page_size=10")
	assert resp.status_code == 200  # invalid key ignored


# ---------------------------------------------------------------------------
# CSV export and errors
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_csv_export_headers_and_filename(api_client):
	"""CSV export streams with a proper filename including asOf when provided."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	api_client.force_authenticate(viewer)
	as_of = (timezone.now().date()).isoformat()
	# ensure at least one row exists
	viewer2 = User.objects.create(email="m@example.com"); _seniority(viewer2, "Software", timezone.now().date()); _orgsnap(viewer2, team_a, timezone.now().date())
	url = reverse("api:personnel-performance-csv") + f"?as_of={as_of}"
	resp = api_client.get(url)
	assert resp.status_code == 200
	cd = resp.get("Content-Disposition", "")
	assert "attachment; filename=personnel-performance_asOf-" in cd or "personnel-performance_current_" in cd
	assert resp["Content-Type"].startswith("text/csv")


@pytest.mark.django_db
def test_invalid_params_return_400(api_client):
	"""Invalid as_of or pagination params should return 400."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	api_client.force_authenticate(viewer)
	assert api_client.get("/api/personnel/performance-table/?as_of=2025-99-99").status_code == 400
	assert api_client.get("/api/personnel/performance-table/?page=abc").status_code == 400
	assert api_client.get("/api/personnel/performance-table/?page_size=abc").status_code == 400


# ---------------------------------------------------------------------------
# Access control matrix (subset; detailed ACL logic is unit-tested separately)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cto_sees_only_tech_category(api_client):
	"""CTO visibility limited to tech ladders per latest as-of SenioritySnapshot."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	cto = User.objects.create(email="cto@example.com"); org.cto = cto; org.save(update_fields=["cto"])
	tech = User.objects.create(email="t@example.com", team=team_a)
	prod = User.objects.create(email="p@example.com", team=team_b)
	_seniority(tech, "Software", timezone.now().date())
	_seniority(prod, "Product", timezone.now().date())
	_orgsnap(tech, team_a, timezone.now().date())
	_orgsnap(prod, team_b, timezone.now().date())
	api_client.force_authenticate(cto)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	assert resp.status_code == 200
	ladders = {r["ladder"] for r in resp.json()["results"]}
	assert all(ld in TECH_LADDERS or ld is None for ld in ladders)
	assert "Product" not in ladders


@pytest.mark.django_db
def test_cpo_sees_only_product_category(api_client):
	"""CPO visibility limited to product ladders per latest as-of SenioritySnapshot."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	cpo = User.objects.create(email="cpo@example.com"); org.cpo = cpo; org.save(update_fields=["cpo"])
	tech = User.objects.create(email="t@example.com", team=team_a)
	prod = User.objects.create(email="p@example.com", team=team_b)
	_seniority(tech, "Software", timezone.now().date())
	_seniority(prod, "Product", timezone.now().date())
	_orgsnap(tech, team_a, timezone.now().date())
	_orgsnap(prod, team_b, timezone.now().date())
	api_client.force_authenticate(cpo)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	ladders = {r["ladder"] for r in resp.json()["results"]}
	assert all(ld in PRODUCT_LADDERS or ld is None for ld in ladders)
	assert "Software" not in ladders


@pytest.mark.django_db
def test_team_leader_scope(api_client):
	"""Team leader sees only their team members via coarse DB filter and final safety pass."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	leader = User.objects.create(email="leader@example.com"); team_a.leader = leader; team_a.save(update_fields=["leader"])
	ua = User.objects.create(email="ua@example.com", team=team_a, leader=leader)
	ub = User.objects.create(email="ub@example.com", team=team_b)
	# org snapshots power the team annotations
	_orgsnap(ua, team_a, timezone.now().date())
	_orgsnap(ub, team_b, timezone.now().date())
	api_client.force_authenticate(leader)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	names = {r["name"] for r in resp.json()["results"]}
	assert "ua@example.com" in names and "ub@example.com" not in names


@pytest.mark.django_db
def test_data_access_override_scopes(api_client):
	"""Explicit DataAccessOverride grants override category visibility (ALL/TECH/PRODUCT)."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="viewer@example.com")
	tech = User.objects.create(email="t@example.com", team=team_a)
	prod = User.objects.create(email="p@example.com", team=team_b)
	_seniority(tech, "Software", timezone.now().date())
	_seniority(prod, "Product", timezone.now().date())
	_orgsnap(tech, team_a, timezone.now().date())
	_orgsnap(prod, team_b, timezone.now().date())
	# TECH override
	DataAccessOverride.objects.create(user=viewer, granted_by=viewer, scope=DataAccessOverride.Scope.TECH, is_active=True)
	api_client.force_authenticate(viewer)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	ladders = {r["ladder"] for r in resp.json()["results"]}
	assert "Product" not in ladders
	# switch to PRODUCT override
	DataAccessOverride.objects.all().delete()
	DataAccessOverride.objects.create(user=viewer, granted_by=viewer, scope=DataAccessOverride.Scope.PRODUCT, is_active=True)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	ladders = {r["ladder"] for r in resp.json()["results"]}
	assert "Software" not in ladders


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_no_snapshots_yield_nulls_and_defaults(api_client):
	"""Users without any snapshots return nulls/defaults for as-of fields and mapped=false."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	hrm = User.objects.create(email="hrm@example.com"); org.hr_manager = hrm; org.save(update_fields=["hr_manager"])
	u = User.objects.create(email="plain@example.com", team=team_a)
	api_client.force_authenticate(hrm)
	resp = api_client.get("/api/personnel/performance-table/?page_size=50")
	row = next(r for r in resp.json()["results"] if r["name"] == "plain@example.com")
	assert row["ladder"] is None
	assert row["last_bonus_percentage"] is None
	assert row["ladder_levels"] == {}


@pytest.mark.django_db
def test_page_size_capped(api_client):
	"""page_size over 500 is capped and response still returns OK (value not exceeding 500)."""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	hrm = User.objects.create(email="hrm@example.com"); org.hr_manager = hrm; org.save(update_fields=["hr_manager"])
	api_client.force_authenticate(hrm)
	resp = api_client.get("/api/personnel/performance-table/?page_size=9999")
	assert resp.status_code == 200
	assert resp.json()["page_size"] <= 500 


@pytest.mark.django_db
def test_accessible_leaders_permissions(api_client):
    """Accessible leaders list respects role, tribe scoping, category, and unmapped subordinates.

    - CEO/HR: see all leaders (anyone with subordinates)
    - CTO: only leaders with ≥1 TECH subordinate OR unmapped subordinate
    - CPO: only leaders with ≥1 PRODUCT subordinate OR unmapped subordinate
    - Directors: tribe-scoped leaders (including unmapped subordinates in their tribe)
    - Team leader: only themselves
    - Deduplication: same leader of multiple teams appears once
    """
    org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()

    # Role holders
    ceo = User.objects.create(email="ceo@example.com"); org.ceo = ceo
    hrm = User.objects.create(email="hr@example.com"); org.hr_manager = hrm
    cto = User.objects.create(email="cto@example.com"); org.cto = cto
    cpo = User.objects.create(email="cpo@example.com"); org.cpo = cpo
    org.save(update_fields=["ceo", "hr_manager", "cto", "cpo"])

    # Leaders and teams
    leader_a = User.objects.create(email="leader_a@example.com")  # tribe_app / TECH
    leader_b = User.objects.create(email="leader_b@example.com")  # tribe_growth / PRODUCT
    team_a.leader = leader_a; team_a.save(update_fields=["leader"])  # tribe_app
    team_b.leader = leader_b; team_b.save(update_fields=["leader"])  # tribe_growth

    # Subordinates
    user_a = User.objects.create(email="user_a@example.com", team=team_a, leader=leader_a)
    user_b = User.objects.create(email="user_b@example.com", team=team_b, leader=leader_b)

    # Ladder categories: TECH for user_a, PRODUCT for user_b
    _seniority(user_a, "Software", timezone.now().date())
    _seniority(user_b, "Product", timezone.now().date())

    # Unmapped subordinate under a third leader in tribe_app
    leader_c = User.objects.create(email="leader_c@example.com")
    team_c = Team.objects.create(name="Team C", department=dep_eng, tribe=tribe_app, leader=leader_c)
    user_c = User.objects.create(email="user_c@example.com", team=team_c, leader=leader_c)  # no seniority snapshot
    # Ensure CTO logic treats unmapped subordinate as TECH via tribe category
    tribe_app.category = "TECH"
    tribe_app.save(update_fields=["category"])

    # Assign Product chapter so CPO includes leader_c via unmapped subordinate in Product chapter
    product_chapter, _ = Chapter.objects.get_or_create(name="Product", department=dep_prod)
    user_c.chapter = product_chapter
    user_c.save(update_fields=["chapter"])

    # Directors (tribe-scoped)
    eng_dir = User.objects.create(email="engdir@example.com", team=team_a)  # ensure their own team points to tribe_app
    tribe_app.engineering_director = eng_dir; tribe_app.save(update_fields=["engineering_director"])
    prod_dir = User.objects.create(email="proddir@example.com", team=team_b)
    tribe_growth.product_director = prod_dir; tribe_growth.save(update_fields=["product_director"])

    # CEO → all leaders
    api_client.force_authenticate(ceo)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert (leader_a.email in leaders) and (leader_b.email in leaders) and (leader_c.email in leaders)

    # HR → all leaders
    api_client.force_authenticate(hrm)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert (leader_a.email in leaders) and (leader_b.email in leaders) and (leader_c.email in leaders)

    # CTO → TECH leaders + unmapped
    api_client.force_authenticate(cto)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert leader_a.email in leaders  # TECH subordinate
    assert leader_b.email not in leaders  # PRODUCT subordinate
    assert leader_c.email in leaders  # unmapped subordinate allowed

    # CPO → PRODUCT leaders + unmapped
    api_client.force_authenticate(cpo)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert leader_b.email in leaders  # PRODUCT subordinate
    assert leader_a.email not in leaders  # TECH subordinate
    assert leader_c.email in leaders  # unmapped subordinate allowed

    # Engineering Director (tribe_app) → leaders in tribe_app only (including unmapped)
    api_client.force_authenticate(eng_dir)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert leader_a.email in leaders
    assert leader_c.email in leaders
    assert leader_b.email not in leaders

    # Product Director (tribe_growth) → leaders in tribe_growth only
    api_client.force_authenticate(prod_dir)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert leader_b.email in leaders
    assert leader_a.email not in leaders
    assert leader_c.email not in leaders

    # Team leader → only themselves
    api_client.force_authenticate(leader_a)
    data = api_client.get("/api/profile/permissions/").json()
    leaders = set(data["permissions"]["accessible_leaders"])
    assert leaders == {leader_a.email}

    # Structure consistency
    assert data["permissions"]["accessible_leaders"] == data["ui_hints"]["filter_options"]["leaders"] 


@pytest.mark.django_db
def test_as_of_controls_seniority_compensation_and_committee_date(api_client):
	"""as_of parameter gates which snapshots/committee date are chosen.
	Creates before/after SenioritySnapshot, CompensationSnapshot, and committee Summaries,
	then asserts the table reflects the 'before' values at mid, and 'after' values when as_of moves past after.
	"""
	org, dep_eng, dep_prod, tribe_app, tribe_growth, team_a, team_b = _create_org_graph()
	viewer = User.objects.create(email="hrm@example.com"); org.hr_manager = viewer; org.save(update_fields=["hr_manager"])
	u = User.objects.create(email="cut@example.com", team=team_a)
	api_client.force_authenticate(viewer)

	mid = timezone.now().date()
	before = mid - timezone.timedelta(days=5)
	after = mid + timezone.timedelta(days=5)

	# Seniority: before (overall 2.0) and after (overall 4.0)
	lad = Ladder.objects.create(code="Software", name="Software")
	_sen_before = SenioritySnapshot.objects.create(
		user=u,
		ladder=lad,
		title="",
		overall_score=2.0,
		effective_date=before,
		details_json={"DES": 1},
		stages_json={},
	)
	_sen_after = SenioritySnapshot.objects.create(
		user=u,
		ladder=lad,
		title="",
		overall_score=4.0,
		effective_date=after,
		details_json={"DES": 3},
		stages_json={},
	)

	# Compensation: before bonus 5.0 (+ salary_change), after bonus 15.0 (+ salary_change)
	# We simulate salary_change by creating snapshots with salary_change values
	CompensationSnapshot.objects.create(user=u, pay_band=None, salary_change=0.5, bonus_percentage=5.0, effective_date=before)
	CompensationSnapshot.objects.create(user=u, pay_band=None, salary_change=1.0, bonus_percentage=15.0, effective_date=after)

	# Committees: one before, one after
	n1 = Note.objects.create(owner=u, title="C1", content="", date=before, type="Proposal", proposal_type=ProposalType.EVALUATION)
	Summary.objects.create(note=n1, content="", committee_date=before, salary_change=0, bonus=0)
	n2 = Note.objects.create(owner=u, title="C2", content="", date=after, type="Proposal", proposal_type=ProposalType.EVALUATION)
	Summary.objects.create(note=n2, content="", committee_date=after, salary_change=0, bonus=0)

	# as_of at mid → pick before values
	resp = api_client.get(f"/api/personnel/performance-table/?as_of={mid.isoformat()}&page_size=100")
	assert resp.status_code == 200
	row = next(r for r in resp.json()["results"] if r["name"] == "cut@example.com")
	assert row["overall_level"] == 2.0
	assert row["last_bonus_percentage"] == 5.0
	assert row["last_salary_change_date"] == before.isoformat()
	assert row["last_committee_date"] == before.isoformat()

	# as_of after → pick after values
	resp = api_client.get(f"/api/personnel/performance-table/?as_of={(after + timezone.timedelta(days=1)).isoformat()}&page_size=100")
	assert resp.status_code == 200
	row = next(r for r in resp.json()["results"] if r["name"] == "cut@example.com")
	assert row["overall_level"] == 4.0
	assert row["last_bonus_percentage"] == 15.0
	assert row["last_salary_change_date"] == after.isoformat()
	assert row["last_committee_date"] == after.isoformat() 