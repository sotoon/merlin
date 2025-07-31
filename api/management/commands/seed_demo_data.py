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

    # No arguments: command always resets demo data

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
        self.stdout.write(self.style.WARNING("حذف داده‌های دمو قبلی…"))
        self._reset()

        self._seed_org()

        # Ensure there is an active performance cycle
        from api.models import Cycle
        from django.utils import timezone
        from datetime import timedelta

        # First, deactivate all existing cycles
        Cycle.objects.filter(is_active=True).update(is_active=False)

        # Then create or update the active cycle
        Cycle.objects.update_or_create(
            is_active=True,
            defaults={
                "name": "دوره فعلی",
                "start_date": timezone.now(),
                "end_date": timezone.now() + timedelta(days=90),
            },
        )

        ladders = self._seed_ladders()
        self._seed_pay_bands()
        leader, member = self._seed_users()
        self._seed_seniority_snapshot(member, ladders[0])
        self._seed_seniority_snapshot(leader, ladders[0])
        self._seed_compensation_snapshot(member)
        self._seed_notice(member, leader)
        self._seed_stock_grant(member, leader)
        self._seed_title_change(member, leader)
        self._seed_timeline_events(member, leader)

        # Add timeline events for leader as well
        self._seed_timeline_events(leader, leader)
        self._seed_leader_timeline_events(leader, leader)

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded ✔"))

    # ------------------------------------------------------------------
    # Delete previously seeded objects
    # ------------------------------------------------------------------

    def _reset(self):
        # Delete timeline events first to avoid foreign key constraints
        from api.models import TimelineEvent

        TimelineEvent.objects.all().delete()

        SenioritySnapshot.objects.all().delete()
        CompensationSnapshot.objects.all().delete()
        Notice.objects.all().delete()
        StockGrant.objects.all().delete()
        TitleChange.objects.all().delete()

        User.objects.filter(
            email__in=[
                "leader@example.com",
                "member@example.com",
            ]
        ).delete()
        Team.objects.filter(name="API").delete()
        Tribe.objects.filter(name="Backend").delete()
        Department.objects.filter(name="Engineering").delete()
        Organization.objects.filter(name="Merlin Demo Org").delete()
        LadderLevel.objects.filter(
            ladder__code__in=[c for c, _ in self.LADDER_CODES]
        ).delete()
        LadderAspect.objects.filter(
            ladder__code__in=[c for c, _ in self.LADDER_CODES]
        ).delete()
        Ladder.objects.filter(code__in=[c for c, _ in self.LADDER_CODES]).delete()
        PayBand.objects.filter(number__lte=10).delete()

    # ------------------------------------------------------------------
    # Seed core organization hierarchy
    # ------------------------------------------------------------------

    def _seed_org(self):
        org, _ = Organization.objects.get_or_create(name="Merlin Demo Org")
        dept, _ = Department.objects.get_or_create(name="Engineering")
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
        leader, created_leader = User.objects.get_or_create(
            email="leader@example.com",
            defaults={
                "username": "leader",
                "name": "Team Leader",
                "is_staff": True,
            },
        )
        if created_leader or not leader.has_usable_password():
            leader.set_password("pw")
            leader.save(update_fields=["password"])

        member, created_member = User.objects.get_or_create(
            email="member@example.com",
            defaults={
                "username": "member",
                "name": "Team Member",
                "leader": leader,
                "team": team,
            },
        )
        if created_member or not member.has_usable_password():
            member.set_password("pw")
            member.save(update_fields=["password"])

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
    # Seed comprehensive timeline events
    # ------------------------------------------------------------------

    def _seed_timeline_events(self, user: User, created_by: User):
        """Create a variety of timeline events with different dates to simulate a realistic career timeline."""
        from api.models import TimelineEvent, EventType
        from datetime import timedelta

        # Get current date and create events going back in time
        today = timezone.now().date()

        # Timeline events with different dates (going back in time)
        timeline_events = [
            {
                "event_type": EventType.TITLE_CHANGE,
                "summary_text": "Junior Developer → Developer",
                "effective_date": today - timedelta(days=365),  # 1 year ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – لدر SW / پاداش ۵٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=300),  # 10 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۵۰ سهم RSU اعطا شد - برنامه واگذاری ۴ ساله",
                "effective_date": today - timedelta(days=280),  # 9 months ago
            },
            {
                "event_type": EventType.PAY_CHANGE,
                "summary_text": "افزایش پله‌ی حقوقی از ۳ به ۴",
                "effective_date": today - timedelta(days=250),  # 8 months ago
            },
            {
                "event_type": EventType.BONUS_PAYOUT,
                "summary_text": "پرداخت پاداش سالانه - ۸٪ از حقوق",
                "effective_date": today - timedelta(days=200),  # 6.5 months ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - بهبود عالی در API",
                "effective_date": today - timedelta(days=150),  # 5 months ago
            },
            {
                "event_type": EventType.SENIORITY_CHANGE,
                "summary_text": "افزایش سطح ارشدیت - رهبری فنی +۱",
                "effective_date": today - timedelta(days=120),  # 4 months ago
            },
            {
                "event_type": EventType.MAPPING,
                "summary_text": "مپ به لدر نرم‌افزار - سطح ۳",
                "effective_date": today - timedelta(days=90),  # 3 months ago
            },
            {
                "event_type": EventType.EVALUATION,
                "summary_text": "نتیجه کمیته – لدر SW / پاداش ۸٪ / پله حقوقی ↑",
                "effective_date": today - timedelta(days=60),  # 2 months ago
            },
            {
                "event_type": EventType.STOCK_GRANT,
                "summary_text": "۲۵ سهم RSU اضافی - پاداش عملکرد",
                "effective_date": today - timedelta(days=45),  # 1.5 months ago
            },
            {
                "event_type": EventType.TITLE_CHANGE,
                "summary_text": "برنامه‌نویس → برنامه‌نویس ارشد",
                "effective_date": today - timedelta(days=30),  # 1 month ago
            },
            {
                "event_type": EventType.PAY_CHANGE,
                "summary_text": "افزایش پله‌ی حقوقی از ۴ به ۵",
                "effective_date": today - timedelta(days=15),  # 2 weeks ago
            },
            {
                "event_type": EventType.NOTICE,
                "summary_text": "نوتیس عملکردی - رهبری برجسته در پروژه‌های تیمی",
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

    # ------------------------------------------------------------------
    # Seed leader-specific timeline events
    # ------------------------------------------------------------------

    def _seed_leader_timeline_events(self, user: User, created_by: User):
        """Create timeline events specific to a team leader role."""
        from api.models import TimelineEvent, EventType
        from datetime import timedelta

        # Get current date and create events going back in time
        today = timezone.now().date()

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
