import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import (
    Organization,
    Department,
    Chapter,
    Tribe,
    Team,
    User,
    Ladder,
    CompensationSnapshot,
    SenioritySnapshot,
    OrgAssignmentSnapshot,
    PayBand,
    Note,
    Summary,
    ProposalType,
    TimelineEvent,
    Notice,
    StockGrant,
    TitleChange,
)
from api.services.timeline_access import TECH_LADDERS, PRODUCT_LADDERS
from api.utils.performance_tables import get_persian_year_bounds_gregorian


FIRST_NAMES = [
    "Ali", "Sara", "Reza", "Mina", "Amir", "Neda", "Hossein", "Leila", "Pouya", "Maryam",
    "Sina", "Fatemeh", "Mahdi", "Zahra", "Navid", "Parisa", "Kaveh", "Elham", "Arash", "Niloufar",
]
LAST_NAMES = [
    "Amiri", "Hosseini", "Ahmadi", "Karimi", "Mohammadi", "Moradi", "Rahimi", "Ebrahimi", "Jafari", "Rezayi",
    "Kazemi", "Ghasemi", "Heydari", "Zare", "Esfahani", "Mehrabi", "Noori", "Najafi", "Soleimani", "Shirazi",
]


@dataclass
class SeedConfig:
    user_count: int = 250
    tech_ratio: float = 0.65
    product_ratio: float = 0.15
    nontech_ratio: float = 0.20


def _random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _random_email(idx: int) -> str:
    return f"user{idx:03d}@example.com"


def _random_pay_band() -> float:
    # 20.0 to 35.0, with 0.5 increments
    base = random.randint(40, 70) / 2.0
    return round(base, 1)


def _rand_date_in_range(start: date, end: date) -> date:
    if start > end:
        start, end = end, start
    delta_days = (end - start).days
    if delta_days <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta_days))


class Command(BaseCommand):
    help = "Seed performance table demo data: users, org structure, ladders, snapshots, committees."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=250, help="Number of users to create")

    @transaction.atomic
    def handle(self, *args, **options):
        cfg = SeedConfig(user_count=int(options.get("users", 250)))

        random.seed(42)
        today = date.today()
        cur_start, cur_end = get_persian_year_bounds_gregorian(today)
        last_start, last_end = get_persian_year_bounds_gregorian(cur_start - timedelta(days=1))

        # Reset previous demo data for idempotency
        self.stdout.write("Clearing existing demo data…")
        # Timeline/artefact tables first to avoid ProtectedError
        TimelineEvent.objects.all().delete()
        Notice.objects.all().delete()
        StockGrant.objects.all().delete()
        TitleChange.objects.all().delete()
        # Child objects
        Summary.objects.all().delete()
        Note.objects.all().delete()
        CompensationSnapshot.objects.all().delete()
        SenioritySnapshot.objects.all().delete()
        OrgAssignmentSnapshot.objects.all().delete()
        # Org structure next
        Team.objects.all().delete()
        Tribe.objects.all().delete()
        Chapter.objects.all().delete()
        Department.objects.all().delete()
        Organization.objects.all().delete()
        # Reference data / pay bands
        PayBand.objects.all().delete()
        # Users (keep superusers like admin)
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Creating organization structure…")
        org, _ = Organization.objects.get_or_create(name="Demo Org")
        dep_eng, _ = Department.objects.get_or_create(name="Engineering")
        dep_prod, _ = Department.objects.get_or_create(name="Product")
        dep_hr, _ = Department.objects.get_or_create(name="HR")
        dep_admin, _ = Department.objects.get_or_create(name="Administration")

        chap_sw, _ = Chapter.objects.get_or_create(name="Software", department=dep_eng)
        chap_ops, _ = Chapter.objects.get_or_create(name="Operations", department=dep_eng)
        chap_prod, _ = Chapter.objects.get_or_create(name="Product", department=dep_prod)

        tribe_app, _ = Tribe.objects.get_or_create(name="App", department=dep_eng)
        tribe_platform, _ = Tribe.objects.get_or_create(name="Platform", department=dep_eng)
        tribe_growth, _ = Tribe.objects.get_or_create(name="Growth", department=dep_prod)

        teams = [
            Team.objects.get_or_create(name="App Core", department=dep_eng, tribe=tribe_app)[0],
            Team.objects.get_or_create(name="App UX", department=dep_eng, tribe=tribe_app)[0],
            Team.objects.get_or_create(name="Platform Infra", department=dep_eng, tribe=tribe_platform)[0],
            Team.objects.get_or_create(name="Platform DevEx", department=dep_eng, tribe=tribe_platform)[0],
            Team.objects.get_or_create(name="Growth Insights", department=dep_prod, tribe=tribe_growth)[0],
            Team.objects.get_or_create(name="Growth Monetization", department=dep_prod, tribe=tribe_growth)[0],
        ]

        self.stdout.write("Ensuring ladders exist…")
        ladder_codes = sorted(set(list(TECH_LADDERS) + list(PRODUCT_LADDERS) + ["HR Ladder", "Administration Ladder"]))
        code_to_ladder = {}
        for code in ladder_codes:
            ladder, _ = Ladder.objects.get_or_create(code=code, defaults={"name": code})
            code_to_ladder[code] = ladder

        self.stdout.write("Creating pay bands…")
        for n in [x / 2.0 for x in range(40, 81)]:  # 20.0 .. 40.0
            PayBand.objects.get_or_create(number=round(n, 1))

        self.stdout.write("Creating leader users…")
        leaders: List[User] = []
        for i in range(1, 21):
            u, _ = User.objects.get_or_create(
                email=_random_email(1000 + i),
                defaults={
                    "name": f"Leader {i}",
                    "department": random.choice([dep_eng, dep_prod, dep_hr, dep_admin]),
                    "chapter": random.choice([chap_sw, chap_ops, chap_prod]),
                    "team": random.choice(teams),
                    "organization": org,
                },
            )
            leaders.append(u)
        # assign team leaders
        for t in teams:
            t.leader = random.choice(leaders)
            t.save(update_fields=["leader"])

        self.stdout.write(f"Creating {cfg.user_count} users…")
        users: List[User] = []
        for i in range(cfg.user_count):
            dept = random.choices([dep_eng, dep_prod, dep_hr, dep_admin], weights=[60, 20, 10, 10])[0]
            chapter = random.choice([chap_sw, chap_ops, chap_prod])
            team = random.choice(teams)
            leader = team.leader
            u, _ = User.objects.get_or_create(
                email=_random_email(i),
                defaults={
                    "name": _random_name(),
                    "department": dept,
                    "chapter": chapter,
                    "team": team,
                    "leader": leader,
                    "organization": org,
                },
            )
            users.append(u)

        # Assign organization-wide executive roles
        self.stdout.write("Assigning executive roles (CEO, CTO, CPO, HR Manager)…")
        admin_user = User.objects.filter(is_superuser=True).order_by("id").first()
        # Prefer picking from relevant departments
        def pick_from(users_qs, fallback_list):
            user = users_qs.order_by("?").first()
            return user or (fallback_list[0] if fallback_list else None)

        org.ceo = admin_user or (leaders[0] if leaders else None)
        org.cto = pick_from(User.objects.filter(department=dep_eng), leaders) or org.ceo
        org.cpo = pick_from(User.objects.filter(department=dep_prod), leaders) or org.ceo
        org.hr_manager = pick_from(User.objects.filter(department=dep_hr), leaders) or org.ceo
        org.save(update_fields=["ceo", "cto", "cpo", "hr_manager"])

        # Deterministic emails and names for role holders (keep admin email)
        if org.cto:
            org.cto.email = "cto@example.com"
            org.cto.name = org.cto.name or "CTO"
            org.cto.set_password("demo1234")
            org.cto.save(update_fields=["email", "name", "password"])
        if org.cpo:
            org.cpo.email = "cpo@example.com"
            org.cpo.name = org.cpo.name or "CPO"
            org.cpo.set_password("demo1234")
            org.cpo.save(update_fields=["email", "name", "password"])
        if org.hr_manager:
            org.hr_manager.email = "hrm@example.com"
            org.hr_manager.name = org.hr_manager.name or "HR Manager"
            org.hr_manager.set_password("demo1234")
            org.hr_manager.save(update_fields=["email", "name", "password"])

        # Assign tribe directors
        self.stdout.write("Assigning tribe directors (Engineering/Product Directors)…")
        for tribe in [tribe_app, tribe_platform]:
            tribe.engineering_director = pick_from(User.objects.filter(department=dep_eng, team__tribe=tribe), leaders) or org.cto
            tribe.save(update_fields=["engineering_director"])
        for tribe in [tribe_growth]:
            tribe.product_director = pick_from(User.objects.filter(department=dep_prod, team__tribe=tribe), leaders) or org.cpo
            tribe.save(update_fields=["product_director"])

        # Deterministic emails for directors
        if tribe_app and tribe_app.engineering_director:
            tribe_app.engineering_director.email = "engdir_app@example.com"
            tribe_app.engineering_director.name = tribe_app.engineering_director.name or "Engineering Director (App)"
            tribe_app.engineering_director.set_password("demo1234")
            tribe_app.engineering_director.save(update_fields=["email", "name", "password"])
        if tribe_platform and tribe_platform.engineering_director:
            tribe_platform.engineering_director.email = "engdir_platform@example.com"
            tribe_platform.engineering_director.name = tribe_platform.engineering_director.name or "Engineering Director (Platform)"
            tribe_platform.engineering_director.set_password("demo1234")
            tribe_platform.engineering_director.save(update_fields=["email", "name", "password"])
        if tribe_growth and tribe_growth.product_director:
            tribe_growth.product_director.email = "proddir_growth@example.com"
            tribe_growth.product_director.name = tribe_growth.product_director.name or "Product Director (Growth)"
            tribe_growth.product_director.set_password("demo1234")
            tribe_growth.product_director.save(update_fields=["email", "name", "password"])

        # Deterministic email for one team leader (App Core) to test team-scope ACL
        app_core = next((t for t in teams if t.name == "App Core"), None)
        if app_core and app_core.leader:
            app_core.leader.email = "teamlead_app_core@example.com"
            app_core.leader.name = app_core.leader.name or "Team Leader (App Core)"
            app_core.leader.set_password("demo1234")
            app_core.leader.save(update_fields=["email", "name", "password"])

        self.stdout.write("Seeding seniority + compensation snapshots and org assignments…")
        comp_rows = []
        sen_rows = []
        org_rows = []
        for u in users:
            # Ladder assignment based on ratios
            r = random.random()
            if r < cfg.tech_ratio:
                ladder_code = random.choice(list(TECH_LADDERS))
            elif r < cfg.tech_ratio + cfg.product_ratio:
                ladder_code = random.choice(list(PRODUCT_LADDERS))
            else:
                ladder_code = random.choice(["HR Ladder", "Administration Ladder"])  # non-tech
            ladder = code_to_ladder.get(ladder_code)

            # Seniority snapshot (details kept minimal)
            sen_rows.append(
                SenioritySnapshot(
                    user=u,
                    ladder=ladder,
                    title=f"{ladder_code} IC",
                    overall_score=round(random.uniform(1.0, 5.0), 1),
                    details_json={"core": random.randint(1, 5), "comm": random.randint(1, 5)},
                    stages_json={"core": "MID", "comm": "EARLY"},
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

            # Compensation baseline
            pay_band = PayBand.objects.filter(number__isnull=False).order_by("?").first()
            comp_rows.append(
                CompensationSnapshot(
                    user=u,
                    pay_band=pay_band,
                    salary_change=0.0,
                    bonus_percentage=random.choice([0, 5, 10, 0, 0, 15]),
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

            # Org snapshot
            org_rows.append(
                OrgAssignmentSnapshot(
                    user=u,
                    leader=u.leader,
                    team=u.team,
                    tribe=getattr(u.team, "tribe", None),
                    chapter=u.chapter,
                    department=u.department,
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

        SenioritySnapshot.objects.bulk_create(sen_rows, batch_size=500)
        CompensationSnapshot.objects.bulk_create(comp_rows, batch_size=500)
        OrgAssignmentSnapshot.objects.bulk_create(org_rows, batch_size=500)

        self.stdout.write("Creating committee summaries for current and last Persian years…")
        proposal_types = [ProposalType.PROMOTION, ProposalType.EVALUATION, ProposalType.MAPPING]
        notes = []
        summaries = []
        for u in users:
            # Random 0–3 committees this year
            for _ in range(random.randint(0, 3)):
                d = _rand_date_in_range(cur_start, cur_end)
                n = Note(
                    owner=u,
                    title=f"Committee {u.name}",
                    content="",
                    date=d,
                    period=0,
                    year=d.year,
                    type="Proposal",
                    proposal_type=random.choice(proposal_types),
                )
                notes.append(n)
                summaries.append(
                    Summary(
                        note=n,
                        content="",
                        ladder=None,
                        aspect_changes={},
                        bonus=0,
                        salary_change=0,
                        committee_date=d,
                    )
                )
            # Random 0–2 committees last year
            for _ in range(random.randint(0, 2)):
                d = _rand_date_in_range(last_start, last_end)
                n = Note(
                    owner=u,
                    title=f"Committee {u.name}",
                    content="",
                    date=d,
                    period=0,
                    year=d.year,
                    type="Proposal",
                    proposal_type=random.choice(proposal_types),
                )
                notes.append(n)
                summaries.append(
                    Summary(
                        note=n,
                        content="",
                        ladder=None,
                        aspect_changes={},
                        bonus=0,
                        salary_change=0,
                        committee_date=d,
                    )
                )

        Note.objects.bulk_create(notes, batch_size=1000)
        Summary.objects.bulk_create(summaries, batch_size=1000)

        # Attach team leaders from created leaders as user.leader if missing
        for u in users:
            if not u.leader and u.team and u.team.leader:
                u.leader = u.team.leader
                u.save(update_fields=["leader"])

        # Ensure admin user is linked to the org (useful for ACL tests)
        if admin_user:
            admin_user.organization = org
            admin_user.save(update_fields=["organization"])

        self.stdout.write(self.style.SUCCESS(f"Seeded performance demo with {len(users)} users.")) 