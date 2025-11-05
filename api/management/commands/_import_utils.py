import csv
import json
import math
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple

from django.db import transaction


# -------------------------------
# CSV helpers
# -------------------------------


def open_csv(path: str, *, encoding: str = "utf-8", delimiter: str = ",") -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def parse_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_float_or_none(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_json_dict(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    try:
        data = json.loads(value)
        if isinstance(data, dict):
            return data
        return None
    except Exception:
        return None


@dataclass
class RowLog:
    row_index: int
    user_email: Optional[str]
    event_type: Optional[str]
    status: str
    errors: Tuple[str, ...]
    warnings: Tuple[str, ...]
    actions: Dict[str, Any]


def to_jsonl(dct: Dict[str, Any]) -> str:
    return json.dumps(dct, ensure_ascii=False)


@contextmanager
def row_savepoint(using_dry_run: bool):
    if using_dry_run:
        # No real transaction for dry-run, but keep context symmetry
        yield
        return
    sid = transaction.savepoint()
    try:
        yield
        transaction.savepoint_commit(sid)
    except Exception:
        transaction.savepoint_rollback(sid)
        raise


# -------------------------------
# Normalization helpers
# -------------------------------


PERSIAN_STAGE = {
    "EARLY": "ابتدای سطح",
    "MID": "میانه سطح",
    "LATE": "انتهای سطح",
}


def normalize_stage(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = str(value).strip()
    # remove zero-width joiner used in some labels
    v = v.replace("\u200c", "")
    if v in PERSIAN_STAGE.values():
        return v
    upper = v.upper()
    return PERSIAN_STAGE.get(upper, v)


def average_or_none(values: Iterable[float]) -> Optional[float]:
    nums = [x for x in values if isinstance(x, (int, float)) and not math.isnan(x)]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 1)


def approx_equal(a: Optional[float], b: Optional[float], tol: float = 0.00001) -> bool:
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


