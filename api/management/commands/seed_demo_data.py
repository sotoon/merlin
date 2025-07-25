import random
from typing import Dict

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import (
    Organization,
    Department,
    Tribe,
    Team,
    User,
    Ladder,
    LadderAspect,
    LadderLevel,
    LadderStage,
    SenioritySnapshot,
    PayBand,
    CompensationSnapshot,
    Notice,
    NoticeType,
    StockGrant,
    TitleChange,
)


class Command(BaseCommand):
    help = "Seed the database with demo data for manual testing of the Profile Timeline feature. Idempotent (safe to run multiple times)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete previously-seeded demo objects before seeding again.",
        )

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    LADDER_CODES = [
        ("SW", "Software Ladder"),
        ("PD", "Product Ladder"),
    ]
    ASPECTS = [
        ("DES", "Design"),
        ("IMP", "Implementation"),
        ("BUS", "Business Acumen"),
        ("COM", "Communication"),
        ("TL", "Technical Leadership"),
    ]

    def handle(self, *args, **options):
        if options.get("reset"):
            self.stdout.write(self.style.WARNING("Reset flag enabled – deleting existing demo data…"))
            self._reset()

        self._seed_org()
        ladders = self._seed_ladders()
        self._seed_pay_bands()
        leader, member = self._seed_users()
        self._seed_seniority_snapshot(member, ladders[0])
        self._seed_compensation_snapshot(member)
        self._seed_notice(member, leader)
        self._seed_stock_grant(member, leader)
        self._seed_title_change(member, leader)

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded ✔"))

    # ------------------------------------------------------------------
    # Delete previously seeded objects
    # ------------------------------------------------------------------

    def _reset(self):
        SenioritySnapshot.objects.all().delete()
        User.objects.filter(email__in=[
            "leader@example.com",
            "member@example.com",
        ]).delete()
        Team.objects.filter(name="API").delete()
        Tribe.objects.filter(name="Backend").delete()
        Department.objects.filter(name="Engineering").delete()
        Organization.objects.filter(name="Merlin Demo Org").delete()
        LadderLevel.objects.filter(ladder__code__in=[c for c, _ in self.LADDER_CODES]).delete()
        LadderAspect.objects.filter(ladder__code__in=[c for c, _ in self.LADDER_CODES]).delete()
        Ladder.objects.filter(code__in=[c for c, _ in self.LADDER_CODES]).delete()
        PayBand.objects.filter(number__lte=10).delete()
        CompensationSnapshot.objects.all().delete()
        Notice.objects.all().delete()
        StockGrant.objects.all().delete()
        TitleChange.objects.all().delete()

    # ------------------------------------------------------------------
    # Seed core organization hierarchy
    # ------------------------------------------------------------------

    def _seed_org(self):
        org, _ = Organization.objects.get_or_create(name="Merlin Demo Org")
        dept, _ = Department.objects.get_or_create(name="Engineering", organization=org)
        tribe, _ = Tribe.objects.get_or_create(name="Backend", department=dept)
        Team.objects.get_or_create(name="API", tribe=tribe, department=dept)

    # ------------------------------------------------------------------
    # Seed ladders, aspects & levels
    # ------------------------------------------------------------------

    def _seed_ladders(self):
        ladders = []
        for code, name in self.LADDER_CODES:
            ladder, _ = Ladder.objects.get_or_create(code=code, defaults={"name": name})
            ladders.append(ladder)

            # Aspects
            for order, (asp_code, asp_name) in enumerate(self.ASPECTS, start=1):
                aspect, _ = LadderAspect.objects.get_or_create(
                    ladder=ladder,
                    code=asp_code,
                    defaults={"name": asp_name, "order": order},
                )
                # Levels 1-6, stage EARLY
                for lvl in range(1, 7):
                    LadderLevel.objects.get_or_create(
                        ladder=ladder,
                        aspect=aspect,
                        level=lvl,
                        stage=LadderStage.EARLY,
                        defaults={"weight": 1.0},
                    )
        return ladders

    # ------------------------------------------------------------------
    # Pay bands
    # ------------------------------------------------------------------

    def _seed_pay_bands(self):
        for num in range(1, 11):
            PayBand.objects.get_or_create(number=num)

    # ------------------------------------------------------------------
    # Seed users
    # ------------------------------------------------------------------

    def _seed_users(self):
        team = Team.objects.get(name="API")
        leader, _ = User.objects.get_or_create(
            email="leader@example.com",
            defaults={
                "username": "leader",
                "name": "Team Leader",
                "is_staff": True,
            },
        )
        member, _ = User.objects.get_or_create(
            email="member@example.com",
            defaults={
                "username": "member",
                "name": "Team Member",
                "leader": leader,
                "team": team,
            },
        )
        return leader, member

    # ------------------------------------------------------------------
    # Compensation snapshot (demo pay-band & bonus)
    # ------------------------------------------------------------------

    def _seed_compensation_snapshot(self, user: User):
        band = PayBand.objects.order_by("number").first()
        CompensationSnapshot.objects.update_or_create(
            user=user,
            effective_date=timezone.now().date(),
            defaults={
                "pay_band": band,
                "bonus_percentage": 8,
            },
        )

    # ------------------------------------------------------------------
    # Notice (lightweight artefact)
    # ------------------------------------------------------------------

    def _seed_notice(self, user: User, created_by: User):
        Notice.objects.get_or_create(
            user=user,
            notice_type=NoticeType.PERFORMANCE,
            description="Performance Notice – keep up the good work!",
            committee_date=timezone.now().date(),
            created_by=created_by,
        )

    # ------------------------------------------------------------------
    # Stock grant (lightweight artefact)
    # ------------------------------------------------------------------

    def _seed_stock_grant(self, user: User, created_by: User):
        StockGrant.objects.get_or_create(
            user=user,
            description="100 RSUs at cliff.",
            created_by=created_by,
        )

    # ------------------------------------------------------------------
    # Title change (creates TimelineEvent via signal)
    # ------------------------------------------------------------------

    def _seed_title_change(self, user: User, created_by: User):
        TitleChange.objects.get_or_create(
            user=user,
            old_title="Developer",
            new_title="Senior Developer",
            effective_date=timezone.now().date(),
            created_by=created_by,
        )

    # ------------------------------------------------------------------
    # Seed a sample SenioritySnapshot to demo current-level feature
    # ------------------------------------------------------------------

    def _seed_seniority_snapshot(self, user: User, ladder: Ladder):
        details: Dict[str, int] = {
            "Design": 3,
            "Implementation": 3,
            "Business Acumen": 2,
            "Communication": 2,
            "Technical Leadership": 2,
        }
        overall = round(sum(details.values()) / len(details), 1)

        SenioritySnapshot.objects.update_or_create(
            user=user,
            ladder=ladder,
            effective_date=timezone.now().date(),
            defaults={
                "title": "",
                "overall_score": overall,
                "details_json": details,
            },
        ) 