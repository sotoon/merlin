import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction, models

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
    OrgValueTag,
    LadderLevel,
    LadderStage,
)
from api.models.ladder import LadderAspect
from api.models.timeline import EventType
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
        OrgValueTag.objects.all().delete()
        Team.objects.all().delete()
        Tribe.objects.all().delete()
        Chapter.objects.all().delete()
        Department.objects.all().delete()
        Organization.objects.all().delete()
        # Reference data / pay bands
        PayBand.objects.all().delete()
        LadderLevel.objects.all().delete() # Added for idempotency
        
        # Delete specific demo users to avoid conflicts
        User.objects.filter(email__in=[
            "leader@example.com",
            "member@example.com", 
            "maintainer@example.com",
            "cto@example.com",
            "cpo@example.com",
            "hrm@example.com",
            "teamlead_app_core@example.com",
            "engdir_app@example.com",
            "engdir_platform@example.com",
            "proddir_growth@example.com"
        ]).delete()
        
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
        # Non-technical tribes
        tribe_finance, _ = Tribe.objects.get_or_create(name="Finance", department=dep_admin)
        tribe_ops_hr, _ = Tribe.objects.get_or_create(name="Operations", department=dep_admin)

        teams = [
            Team.objects.get_or_create(name="App Core", department=dep_eng, tribe=tribe_app)[0],
            Team.objects.get_or_create(name="App UX", department=dep_eng, tribe=tribe_app)[0],
            Team.objects.get_or_create(name="Platform Infra", department=dep_eng, tribe=tribe_platform)[0],
            Team.objects.get_or_create(name="Platform DevEx", department=dep_eng, tribe=tribe_platform)[0],
            Team.objects.get_or_create(name="Growth Insights", department=dep_prod, tribe=tribe_growth)[0],
            Team.objects.get_or_create(name="Growth Monetization", department=dep_prod, tribe=tribe_growth)[0],
            # Non-tech teams
            Team.objects.get_or_create(name="Accounting", department=dep_admin, tribe=tribe_finance)[0],
            Team.objects.get_or_create(name="Payroll", department=dep_admin, tribe=tribe_finance)[0],
            Team.objects.get_or_create(name="Office Ops", department=dep_admin, tribe=tribe_ops_hr)[0],
        ]

        self.stdout.write("Ensuring ladders exist…")
        ladder_codes = sorted(set(list(TECH_LADDERS) + list(PRODUCT_LADDERS) + ["HR Ladder", "Administration Ladder"]))
        code_to_ladder = {}
        for code in ladder_codes:
            ladder, _ = Ladder.objects.get_or_create(code=code, defaults={"name": code})
            code_to_ladder[code] = ladder

        # Define aspects for different ladder types
        
        # Technical ladder aspects (similar for all tech ladders)
        tech_aspects = [
            ("technical", "مهارت‌های فنی", 1),
            ("leadership", "رهبری", 2),
            ("communication", "ارتباطات", 3),
            ("delivery", "تحویل و تأثیر", 4),
            ("collaboration", "همکاری", 5),
        ]
        
        # Product ladder aspects
        product_aspects = [
            ("product_strategy", "استراتژی محصول", 1),
            ("execution", "اجرا", 2),
            ("leadership", "رهبری", 3),
            ("communication", "ارتباطات", 4),
            ("data_analysis", "تحلیل داده", 5),
            ("user_research", "تحقیق کاربر", 6),
        ]
        
        # Non-technical ladder aspects
        nontech_aspects = [
            ("domain_expertise", "تخصص حوزه", 1),
            ("execution", "اجرا", 2),
            ("leadership", "رهبری", 3),
            ("communication", "ارتباطات", 4),
            ("collaboration", "همکاری", 5),
        ]
        
        self.stdout.write("Creating ladder aspects…")
        for code, ladder in code_to_ladder.items():
            # Choose aspects based on ladder type
            if code in TECH_LADDERS:
                aspects = tech_aspects
            elif code in PRODUCT_LADDERS:
                aspects = product_aspects
            else:  # HR Ladder, Administration Ladder
                aspects = nontech_aspects
            
            # Create aspects for this ladder
            for aspect_code, aspect_name, order in aspects:
                LadderAspect.objects.get_or_create(
                    ladder=ladder,
                    code=aspect_code,
                    defaults={
                        "name": aspect_name,
                        "order": order,
                    }
                )

        self.stdout.write("Creating ladder levels…")
        for ladder in code_to_ladder.values():
            aspects = ladder.aspects.all()
            if not aspects:
                continue

            # Random max level between 5 and 6 for each ladder
            max_level = random.randint(5, 6)
            
            for aspect in aspects:
                for level in range(1, max_level + 1):
                    for stage in LadderStage.choices:
                        LadderLevel.objects.get_or_create(
                            ladder=ladder,
                            aspect=aspect,
                            level=level,
                            stage=stage[0],
                        )

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

        # Ensure leaders have baseline snapshots (seniority/compensation/org)
        self.stdout.write("Creating baseline snapshots for leaders…")
        leader_sen_rows = []
        leader_comp_rows = []
        leader_org_rows = []
        for leader in leaders:
            team = leader.team
            tribe = getattr(team, "tribe", None)

            # Pick ladder category based on team/tribe context (tech/product vs non-tech)
            if team and team.department == dep_eng:
                ladder_code = random.choice(list(TECH_LADDERS))
            elif team and team.department == dep_prod:
                ladder_code = random.choice(list(PRODUCT_LADDERS))
            else:
                ladder_code = random.choice(["HR Ladder", "Administration Ladder"])  # non-tech
            ladder = code_to_ladder.get(ladder_code)

            # Build aspect scores similar to regular users
            if ladder:
                aspects = list(ladder.aspects.all())
                if aspects:
                    details_json = {}
                    stages_json = {}
                    # Get max level from ladder levels for this ladder
                    max_level = LadderLevel.objects.filter(ladder=ladder).aggregate(max_level=models.Max('level'))['max_level'] or 5
                    for aspect in aspects:
                        level = random.randint(1, max_level)
                        stage = random.choice(["EARLY", "MID", "LATE"])
                        details_json[aspect.code] = level
                        stages_json[aspect.code] = stage
                    overall_score = round(sum(details_json.values()) / max(1, len(details_json)), 1)
                else:
                    max_level = random.randint(5, 10)  # Random fallback max level
                    details_json = {"core": random.randint(1, max_level), "comm": random.randint(1, max_level)}
                    stages_json = {"core": "MID", "comm": "EARLY"}
                    overall_score = round(random.uniform(1.0, max_level), 1)
            else:
                max_level = random.randint(5, 10)  # Random fallback max level
                details_json = {"core": random.randint(1, max_level), "comm": random.randint(1, max_level)}
                stages_json = {"core": "MID", "comm": "EARLY"}
                overall_score = round(random.uniform(1.0, max_level), 1)

            leader_sen_rows.append(
                SenioritySnapshot(
                    user=leader,
                    ladder=ladder,
                    title=f"{ladder_code} IC" if ladder_code else "IC",
                    overall_score=overall_score,
                    details_json=details_json,
                    stages_json=stages_json,
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

            # Compensation baseline for leader
            pay_band = PayBand.objects.filter(number__isnull=False).order_by("?").first()
            leader_comp_rows.append(
                CompensationSnapshot(
                    user=leader,
                    pay_band=pay_band,
                    salary_change=0.0,
                    bonus_percentage=random.choice([0, 5, 10, 0, 0, 15]),
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

            # Org snapshot for leader
            leader_org_rows.append(
                OrgAssignmentSnapshot(
                    user=leader,
                    leader=leader.leader,
                    team=leader.team,
                    tribe=tribe,
                    chapter=leader.chapter,
                    department=leader.department,
                    effective_date=today - timedelta(days=random.randint(60, 400)),
                )
            )

        if leader_sen_rows:
            SenioritySnapshot.objects.bulk_create(leader_sen_rows, batch_size=500)
        if leader_comp_rows:
            CompensationSnapshot.objects.bulk_create(leader_comp_rows, batch_size=500)
        if leader_org_rows:
            OrgAssignmentSnapshot.objects.bulk_create(leader_org_rows, batch_size=500)

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

        # Create member and leader users (similar to seed_demo_data.py)
        self.stdout.write("Creating member and leader users…")
        
        # Find a technical team for the member and leader
        technical_teams = [t for t in teams if t.department in [dep_eng, dep_prod]]
        if not technical_teams:
            technical_teams = teams  # fallback to any team
        
        member_team = random.choice(technical_teams)
        
        # Create leader user
        leader_user, _ = User.objects.get_or_create(
            email="leader@example.com",
            defaults={
                "name": "Team Leader",
                "department": member_team.department,
                "chapter": chap_sw,
                "team": member_team,
                "organization": org,
            },
        )
        leader_user.set_password("pw")
        leader_user.save(update_fields=["password"])
        
        # Set the leader as the team leader
        member_team.leader = leader_user
        member_team.save(update_fields=["leader"])
        
        # Create member user
        member_user, _ = User.objects.get_or_create(
            email="member@example.com",
            defaults={
                "name": "Team Member",
                "department": member_team.department,
                "chapter": chap_sw,
                "team": member_team,
                "leader": leader_user,
                "organization": org,
                "is_active": True,
            },
        )
        # Always set the password to ensure it's correct
        member_user.set_password("pw")
        member_user.is_active = True
        member_user.save(update_fields=["password", "is_active"])
        
        # Add them to the users list
        users.extend([leader_user, member_user])

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

        # Create maintainer user
        maintainer_user, _ = User.objects.get_or_create(
            email="maintainer@example.com",
            defaults={
                "name": "Maintainer",
                "department": dep_eng,  # Assign to engineering department
                "chapter": chap_sw,
                "team": teams[0] if teams else None,
                "organization": org,
                "is_active": True,
            },
        )
        maintainer_user.set_password("demo1234")
        maintainer_user.save(update_fields=["password"])
        
        # Assign MAINTAINER role to the organization
        org.maintainer = maintainer_user
        org.save(update_fields=["maintainer"])

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
            app_core.leader.username = "teamlead_app_core"  # Set explicit username to avoid conflict
            app_core.leader.set_password("demo1234")
            app_core.leader.save(update_fields=["email", "name", "username", "password"])

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

            # Seniority snapshot with realistic aspect data
            if ladder:
                # Get aspects for this ladder
                aspects = list(ladder.aspects.all())
                if aspects:
                    # Create realistic aspect scores and stages
                    details_json = {}
                    stages_json = {}
                    # Get max level from ladder levels for this ladder
                    max_level = LadderLevel.objects.filter(ladder=ladder).aggregate(max_level=models.Max('level'))['max_level'] or 5
                    for aspect in aspects:
                        level = random.randint(1, max_level)
                        stage = random.choice(["EARLY", "MID", "LATE"])
                        details_json[aspect.code] = level
                        stages_json[aspect.code] = stage
                    
                    overall_score = round(sum(details_json.values()) / len(details_json), 1)
                else:
                    # Fallback if no aspects defined
                    max_level = random.randint(5, 10)  # Random fallback max level
                    details_json = {"core": random.randint(1, max_level), "comm": random.randint(1, max_level)}
                    stages_json = {"core": "MID", "comm": "EARLY"}
                    overall_score = round(random.uniform(1.0, max_level), 1)
            else:
                # Fallback if no ladder assigned
                max_level = random.randint(5, 10)  # Random fallback max level
                details_json = {"core": random.randint(1, max_level), "comm": random.randint(1, max_level)}
                stages_json = {"core": "MID", "comm": "EARLY"}
                overall_score = round(random.uniform(1.0, max_level), 1)
            
            sen_rows.append(
                SenioritySnapshot(
                    user=u,
                    ladder=ladder,
                    title=f"{ladder_code} IC" if ladder_code else "IC",
                    overall_score=overall_score,
                    details_json=details_json,
                    stages_json=stages_json,
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

        # Create timeline events for snapshots (since bulk_create doesn't trigger signals)
        self.stdout.write("Creating timeline events for snapshots…")
        from django.contrib.contenttypes.models import ContentType
        
        timeline_events = []
        
        # Create events for SenioritySnapshots
        for snapshot in SenioritySnapshot.objects.all():
            summary_text = f"سطح ارشدیت کاربر به {snapshot.overall_score} تغییر کرد."
            if snapshot.ladder:
                summary_text += f" لدر: {snapshot.ladder.name}"
            
            content_type = ContentType.objects.get_for_model(SenioritySnapshot)
            timeline_events.append(
                TimelineEvent(
                    user=snapshot.user,
                    event_type=EventType.SENIORITY_CHANGE,
                    summary_text=summary_text,
                    effective_date=snapshot.effective_date,
                    content_type=content_type,
                    object_id=snapshot.pk,
                    visibility_mask=1,
                )
            )
        
        # Create events for CompensationSnapshots
        for snapshot in CompensationSnapshot.objects.all():
            summary_text = f"پله حقوقی کاربر به {snapshot.pay_band.number} تغییر کرد."
            if snapshot.salary_change:
                summary_text += f" تغییر: {snapshot.salary_change:+g}"
            if snapshot.bonus_percentage:
                summary_text += f" پاداش: {snapshot.bonus_percentage}%"
            
            content_type = ContentType.objects.get_for_model(CompensationSnapshot)
            timeline_events.append(
                TimelineEvent(
                    user=snapshot.user,
                    event_type=EventType.PAY_CHANGE,
                    summary_text=summary_text,
                    effective_date=snapshot.effective_date,
                    content_type=content_type,
                    object_id=snapshot.pk,
                    visibility_mask=1,
                )
            )
        
        TimelineEvent.objects.bulk_create(timeline_events, batch_size=500)
        self.stdout.write(f"Created {len(timeline_events)} timeline events")

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

        # Set categories for tribes
        tribe_app.category = "TECH"; tribe_app.save(update_fields=["category"])
        tribe_platform.category = "TECH"; tribe_platform.save(update_fields=["category"])
        tribe_growth.category = "TECH"; tribe_growth.save(update_fields=["category"])
        tribe_finance.category = "NON_TECH"; tribe_finance.save(update_fields=["category"])
        tribe_ops_hr.category = "NON_TECH"; tribe_ops_hr.save(update_fields=["category"])

        # Set categories for teams (override if needed)
        for t in teams:
            if t.tribe == tribe_app or t.tribe == tribe_platform:
                t.category = "TECH"
            elif t.tribe == tribe_growth:
                t.category = "TECH"
            else:
                t.category = "NON_TECH"
            t.save(update_fields=["category"])

        # Create comprehensive timeline events for HR manager (similar to seed_demo_data.py member events)
        if org.hr_manager:
            self.stdout.write("Creating comprehensive timeline events for HR manager...")
            self._seed_hr_manager_timeline_events(org.hr_manager, org.hr_manager)

        # Create comprehensive timeline events for leader user (similar to seed_demo_data.py)
        self.stdout.write("Creating comprehensive timeline events for leader user...")
        leader_user = User.objects.filter(email="leader@example.com").first()
        
        if leader_user:
            self._seed_leader_timeline_events(leader_user, leader_user)

    def _seed_hr_manager_timeline_events(self, user: User, created_by: User):
        """Create comprehensive timeline events for HR manager similar to seed_demo_data.py member events."""
        from datetime import timedelta
        today = date.today()

        # Timeline events with different dates (going back in time) - HR manager specific
        timeline_events = [
            {
                "event_type": EventType.TITLE_CHANGE,
                "summary_text": "HR Specialist → HR Coordinator",
                "effective_date": today - timedelta(days=365),  # 1 year ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – ارزیابی عملکرد HR / پاداش ۱۰٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=300),  # 10 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۷۵ سهم RSU اعطا شد - برنامه واگذاری ۴ ساله",
                "effective_date": today - timedelta(days=280),  # 9 months ago
            },
            {
                "event_type": EventType.PAY_CHANGE,
                "summary_text": "افزایش پله‌ی حقوقی از ۴ به ۵",
                "effective_date": today - timedelta(days=250),  # 8 months ago
            },
            {
                "event_type": EventType.BONUS_PAYOUT,
                "summary_text": "پرداخت پاداش سالانه - ۱۲٪ از حقوق",
                "effective_date": today - timedelta(days=200),  # 6.5 months ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - بهبود فرآیندهای استخدام و onboarding",
                "effective_date": today - timedelta(days=150),  # 5 months ago
            },
            {
                "event_type": EventType.SENIORITY_CHANGE,
                "summary_text": "افزایش سطح ارشدیت - مهارت‌های مدیریت منابع انسانی +۲",
                "effective_date": today - timedelta(days=120),  # 4 months ago
            },
            {
                "event_type": EventType.MAPPING,
                "summary_text": "مپ به لدر مدیریت منابع انسانی - سطح ۴",
                "effective_date": today - timedelta(days=90),  # 3 months ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – ارزیابی عملکرد HR / پاداش ۱۵٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=60),  # 2 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۵۰ سهم RSU اضافی - پاداش عملکرد برجسته",
                "effective_date": today - timedelta(days=45),  # 1.5 months ago
            },
            {
                "event_type": EventType.TITLE_CHANGE,
                "summary_text": "HR Coordinator → HR Manager",
                "effective_date": today - timedelta(days=30),  # 1 month ago
            },
            {
                "event_type": EventType.PAY_CHANGE,
                "summary_text": "افزایش پله‌ی حقوقی از ۵ به ۶ - ارتقای مدیریتی",
                "effective_date": today - timedelta(days=15),  # 2 weeks ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - رهبری برجسته در مدیریت منابع انسانی سازمان",
                "effective_date": today - timedelta(days=7),  # 1 week ago
            },
        ]

        # Create timeline events
        for event_data in timeline_events:
            TimelineEvent.objects.get_or_create(
                user=user,
                event_type=event_data["event_type"],
                summary_text=event_data["summary_text"],
                effective_date=event_data["effective_date"],
                defaults={
                    "created_by": created_by,
                },
            )

        # Create additional HR-specific events
        hr_specific_events = [
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - بهبود فرآیند ارزیابی عملکرد کارکنان",
                "effective_date": today - timedelta(days=180),  # 6 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۲۵ سهم RSU اضافی - پاداش بهبود فرآیندهای HR",
                "effective_date": today - timedelta(days=160),  # 5.5 months ago
            },
            {
                "event_type": EventType.BONUS_PAYOUT,
                "summary_text": "پرداخت پاداش ویژه - ۸٪ از حقوق",
                "effective_date": today - timedelta(days=140),  # 4.5 months ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - موفقیت در پیاده‌سازی سیستم مدیریت عملکرد",
                "effective_date": today - timedelta(days=100),  # 3.5 months ago
            },
        ]

        # Create HR-specific timeline events
        for event_data in hr_specific_events:
            TimelineEvent.objects.get_or_create(
                user=user,
                event_type=event_data["event_type"],
                summary_text=event_data["summary_text"],
                effective_date=event_data["effective_date"],
                defaults={
                    "created_by": created_by,
                },
            )



    def _seed_leader_timeline_events(self, user: User, created_by: User):
        """Create comprehensive timeline events for leader user similar to seed_demo_data.py leader events."""
        from datetime import timedelta
        today = date.today()

        # Leader-specific timeline events
        leader_events = [
            {
                "event_type": EventType.TITLE_CHANGE,
                "summary_text": "Senior Developer → Team Lead",
                "effective_date": today - timedelta(days=400),  # 13 months ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – ارزیابی رهبری / پاداش ۱۲٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=350),  # 11.5 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۱۰۰ سهم RSU اعطا شد - جبران نقش رهبری",
                "effective_date": today - timedelta(days=320),  # 10.5 months ago
            },
            {
                "event_type": EventType.PAY_CHANGE,
                "summary_text": "افزایش پله‌ی حقوقی از ۵ به ۶ - ارتقای رهبری",
                "effective_date": today - timedelta(days=300),  # 10 months ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - رهبری و منتورینگ ضعیف تیم",
                "effective_date": today - timedelta(days=180),  # 6 months ago
            },
            {
                "event_type": EventType.SENIORITY_CHANGE,
                "summary_text": "افزایش سطح ارشدیت - مهارت‌های رهبری +۲",
                "effective_date": today - timedelta(days=150),  # 5 months ago
            },
            {
                "event_type": EventType.BONUS_PAYOUT,
                "summary_text": "پرداخت پاداش رهبری - ۱۵٪ از حقوق",
                "effective_date": today - timedelta(days=120),  # 4 months ago
            },
            {
                "event_type": EventType.MAPPING,
                "summary_text": "مپ به لدر رهبری - سطح ۴",
                "effective_date": today - timedelta(days=90),  # 3 months ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – ارزیابی عملکرد تیم / پاداش ۱۵٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=60),  # 2 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۵۰ سهم RSU اضافی - پاداش موفقیت تیم",
                "effective_date": today - timedelta(days=30),  # 1 month ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - مدیریت تیم و تحویل پروژه غیر قابل قبول",
                "effective_date": today - timedelta(days=10),  # 1.5 weeks ago
            },
        ]

        # Create leader timeline events
        for event_data in leader_events:
            TimelineEvent.objects.get_or_create(
                user=user,
                event_type=event_data["event_type"],
                summary_text=event_data["summary_text"],
                effective_date=event_data["effective_date"],
                defaults={
                    "created_by": created_by,
                },
            )