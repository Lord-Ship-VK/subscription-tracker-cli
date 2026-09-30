"""
Utility functions for validation and formatting, and renewal-date arithmetic.
"""
import calendar
import math
from datetime import datetime, date
from .models import VALID_CATEGORIES, DEFAULT_CATEGORY


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_date(date_str: str) -> str:
    """Validates if a string is a valid YYYY-MM-DD date."""
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        if parsed_date.strftime("%Y-%m-%d") != date_str:
            raise ValueError
        return date_str
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")


def validate_cost(cost: float) -> float:
    """Validates if the cost is a positive number."""
    if not math.isfinite(cost) or cost <= 0:
        raise ValueError("Cost must be positive.")
    return cost


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format an amount using the selected currency without converting it."""
    if currency == "INR":
        return f"INR {amount:.2f}"
    return f"${amount:.2f}"


def validate_name(name: str) -> str:
    """Validates if the name is not empty."""
    if not name.strip():
        raise ValueError("Name cannot be empty.")
    return name


def validate_category(category: str) -> str:
    """
    Validates and normalises a category string.

    Accepts case-insensitive input and returns the correctly-cased canonical
    category name.  Raises ValueError if the category is not recognised.
    """
    normalised = category.strip().title()
    # "Cloud Storage" uses title case so .title() already handles it correctly.
    for valid in VALID_CATEGORIES:
        if valid.lower() == normalised.lower():
            return valid
    raise ValueError(
        f"Invalid category '{category}'. "
        f"Choose from: {', '.join(VALID_CATEGORIES)}"
    )


# ---------------------------------------------------------------------------
# Renewal-date arithmetic (private helpers)
# ---------------------------------------------------------------------------

def _add_months(d: date, months: int) -> date:
    """
    Add ``months`` to a date, clamping the day when the target month is
    shorter than the source month.

    Examples
    --------
    Jan 31 + 1 month → Feb 28  (non-leap year)
    Jan 31 + 1 month → Feb 29  (leap year)
    """
    raw_month = d.month - 1 + months          # zero-indexed
    year  = d.year + raw_month // 12
    month = raw_month % 12 + 1                # back to 1-indexed
    day   = min(d.day, calendar.monthrange(year, month)[1])
    return d.replace(year=year, month=month, day=day)


def _add_years(d: date, years: int) -> date:
    """
    Add ``years`` to a date, clamping Feb 29 to Feb 28 in non-leap years.

    Example
    -------
    Feb 29 2024 + 1 year → Feb 28 2025
    """
    year = d.year + years
    day  = min(d.day, calendar.monthrange(year, d.month)[1])
    return d.replace(year=year, day=day)


# ---------------------------------------------------------------------------
# Renewal-date advancement (public API)
# ---------------------------------------------------------------------------

def advance_renewal_date(date_str: str, cycle: str, reference_date: date = None) -> str:
    """
    Advance a stale renewal date forward by one billing cycle at a time until
    it is on or after ``reference_date`` (defaults to today).

    Rules
    -----
    * If the date is **today or in the future** it is returned unchanged.
    * ``monthly`` subscriptions advance by one calendar month per step,
      with day-clamping at month boundaries (e.g. Jan 31 → Feb 28/29).
    * ``yearly`` subscriptions advance by one calendar year per step,
      with day-clamping for Feb 29 in non-leap years.
    * If ``date_str`` is malformed it is returned as-is; validation is the
      responsibility of the input layer.

    Parameters
    ----------
    date_str       : the stored ``next_date`` string in YYYY-MM-DD format.
    cycle          : ``'monthly'`` or ``'yearly'``.
    reference_date : the date against which staleness is measured.
                     Accepts a ``datetime.date`` object.  Defaults to today.
                     Pass an explicit value in tests to keep results deterministic.

    Returns
    -------
    A ``str`` in YYYY-MM-DD format representing the next valid billing date.
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return date_str  # malformed – return unchanged, let validation handle it

    if dt >= reference_date:
        return date_str  # already today or future – nothing to advance

    if cycle == "monthly":
        while dt < reference_date:
            dt = _add_months(dt, 1)
    elif cycle == "yearly":
        while dt < reference_date:
            dt = _add_years(dt, 1)
    # Unknown cycles are left unchanged (defensive).

    return dt.strftime("%Y-%m-%d")


def refresh_renewal_dates(subscriptions: list, reference_date: date = None) -> bool:
    """
    Advance stale renewal dates on every subscription in ``subscriptions``
    **in-place**, using the same ``reference_date`` for all of them.

    Returns ``True`` if at least one date was changed, ``False`` otherwise.
    The ``reference_date`` parameter defaults to today and can be injected in
    tests for deterministic results.
    """
    changed = False
    for sub in subscriptions:
        new_date = advance_renewal_date(sub.next_date, sub.cycle, reference_date)
        if new_date != sub.next_date:
            sub.next_date = new_date
            changed = True
    return changed
