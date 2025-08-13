from datetime import datetime, date, timedelta
from typing import Optional, Tuple
from persiantools.jdatetime import JalaliDate

__all__ = ["build_csv_filename", "get_persian_year_bounds_gregorian"]


def build_csv_filename(as_of: Optional[str]) -> str:
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if as_of:
        return f"personnel-performance_asOf-{as_of}_{now_str}.csv"
    return f"personnel-performance_current_{now_str}.csv"


def get_persian_year_bounds_gregorian(ref_date: date) -> Tuple[date, date]:
    """Return (start_greg, end_greg) dates bounding the Persian year containing ref_date.
    Uses persiantools for reliable Jalali conversions.
    """
    j = JalaliDate.to_jalali(ref_date)
    start_greg = JalaliDate(j.year, 1, 1).to_gregorian()
    end_greg_exclusive = JalaliDate(j.year + 1, 1, 1).to_gregorian()
    end_greg_inclusive = end_greg_exclusive - timedelta(days=1)
    return start_greg, end_greg_inclusive 