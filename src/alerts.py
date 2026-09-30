"""
Alerts and notifications logic.
"""
from datetime import datetime
from .storage import load_data, get_currency
from .utils import format_currency

def check_alerts():
    """Checks for subscriptions renewing in the next 7 days."""
    subs = load_data()
    today = datetime.now().date()
    upcoming = []

    for sub in subs:
        try:
            next_date = datetime.strptime(sub.next_date, "%Y-%m-%d").date()
            days_until = (next_date - today).days
            if 0 <= days_until <= 7:
                upcoming.append((sub, days_until))
        except ValueError:
            pass

    print("--- Renewal Alerts (Next 7 Days) ---")
    if not upcoming:
        print("No upcoming renewals.")
    else:
        for sub, days in upcoming:
            day_str = "today" if days == 0 else f"in {days} days"
            print(
                f"Alert: {sub.name} renews {day_str} on {sub.next_date} "
                f"for {format_currency(sub.cost, get_currency())}"
            )
