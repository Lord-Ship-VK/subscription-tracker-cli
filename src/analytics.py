"""
Expense analytics logic.
"""
from collections import defaultdict
from .storage import load_data


def monthly_cost(sub) -> float:
    """Returns the monthly equivalent cost of a subscription."""
    if sub.cycle == 'monthly':
        return sub.cost
    elif sub.cycle == 'yearly':
        return sub.cost / 12
    return 0.0


def show_analytics():
    """
    Calculates and displays a rich expense breakdown including:
    - total subscription count
    - total monthly and yearly spending
    - spending grouped by category
    - most expensive subscription
    """
    subs = load_data()

    if not subs:
        print("--- Expense Analytics ---")
        print("No subscriptions found.")
        return

    monthly_total = 0.0
    yearly_total = 0.0
    by_category = defaultdict(float)
    most_expensive = None
    most_expensive_monthly = -1.0

    for sub in subs:
        monthly = monthly_cost(sub)
        monthly_total += monthly
        yearly_total += monthly * 12
        by_category[sub.category] += monthly

        if monthly > most_expensive_monthly:
            most_expensive_monthly = monthly
            most_expensive = sub

    print("--- Expense Analytics ---")
    print(f"Total Subscriptions:   {len(subs)}")
    print(f"Total Monthly Cost:    ${monthly_total:.2f}")
    print(f"Total Yearly Cost:     ${yearly_total:.2f}")

    print("\n  Spending by Category (monthly equivalent):")
    for category, amount in sorted(by_category.items()):
        print(f"    {category:<16} ${amount:.2f}")

    if most_expensive:
        print(
            f"\n  Most Expensive:        {most_expensive.name} "
            f"(${most_expensive_monthly:.2f}/month)"
        )
