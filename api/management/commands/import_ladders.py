from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.management.commands._import_utils import (
    average_or_none,
    normalize_stage,
    open_csv,
    row_savepoint,
)
from api.models.ladder import Ladder, LadderAspect, LadderLevel, LadderStage


class Command(BaseCommand):
    help = "Import ladders, aspects, or levels from separate CSV files. Idempotent, supports dry-run."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Absolute path to CSV file")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--ladders-only", action="store_true", help="Import only ladders section")
        parser.add_argument("--aspects-only", action="store_true", help="Import only aspects section")
        parser.add_argument("--levels-only", action="store_true", help="Import only levels section")

    def handle(self, *args, **options):
        # Django passes dest names without leading dashes
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        ladders_only = bool(options["ladders_only"])
        aspects_only = bool(options["aspects_only"])
        levels_only = bool(options["levels_only"])

        # Validate that exactly one mode is selected
        modes = [ladders_only, aspects_only, levels_only]
        if sum(modes) > 1:
            raise CommandError("Only one of --ladders-only, --aspects-only, or --levels-only can be specified")
        if not any(modes):
            raise CommandError("One of --ladders-only, --aspects-only, or --levels-only must be specified")

        created = updated = skipped = 0

        with transaction.atomic():
            # For consistency, still open a transaction. Writes will be rolled back if dry-run.
            for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=1):
                # Skip completely empty rows
                if not any(row.values()):
                    continue

                # Process based on selected mode
                if ladders_only:
                    # Ladders section
                    if row.get("ladder_code"):
                        with row_savepoint(dry_run):
                            if not dry_run:
                                ladder, ladder_created = Ladder.objects.update_or_create(
                                    code=row["ladder_code"],
                                    defaults={
                                        "name": row.get("ladder_name") or row["ladder_code"],
                                        "description": row.get("ladder_description") or "",
                                    },
                                )
                            else:
                                ladder_created = False
                            created += 1 if ladder_created else 0
                            updated += 0 if ladder_created else 1

                elif aspects_only:
                    # Aspects section
                    if row.get("aspect_code"):
                        with row_savepoint(dry_run):
                            # Get the ladder
                            if not dry_run:
                                ladder = Ladder.objects.get(code=row["ladder_code"])
                            else:
                                ladder = None

                            if not dry_run:
                                # Use persian_name as the name if available, otherwise aspect_name, otherwise aspect_code
                                aspect_display_name = (row.get("persian_name") or
                                                     row.get("aspect_name") or
                                                     row["aspect_code"])
                                aspect, aspect_created = LadderAspect.objects.update_or_create(
                                    ladder=ladder,
                                    code=row["aspect_code"],
                                    defaults={
                                        "name": aspect_display_name,
                                        "order": int(row.get("aspect_order") or 0),
                                    },
                                )
                            else:
                                aspect_created = False
                            created += 1 if aspect_created else 0
                            updated += 0 if aspect_created else 1

                elif levels_only:
                    # Levels section
                    if row.get("level"):
                        with row_savepoint(dry_run):
                            # Get the ladder and aspect
                            if not dry_run:
                                ladder = Ladder.objects.get(code=row["ladder_code"])
                                aspect = LadderAspect.objects.get(ladder=ladder, code=row["aspect_code"])

                                stage_norm = normalize_stage(row.get("stage")) or LadderStage.default()
                                step, step_created = LadderLevel.objects.update_or_create(
                                    ladder=ladder,
                                    aspect=aspect,
                                    level=int(row["level"]),
                                    stage=stage_norm,
                                    defaults={
                                        "weight": float(row.get("weight") or 1.0),
                                    },
                                )
                            else:
                                step_created = False
                            created += 1 if step_created else 0
                            updated += 0 if step_created else 1


            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
        self.stdout.write(self.style.SUCCESS(f"Ladders import finished. created={created}, updated={updated}, skipped={skipped}"))


