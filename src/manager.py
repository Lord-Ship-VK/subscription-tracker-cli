"""
Core business logic for managing subscriptions.
"""
from .storage import load_data, save_data, get_currency
from .models import Subscription, DEFAULT_CATEGORY
from .utils import format_currency


def add_subscription(
    name: str,
    cost: float,
    cycle: str,
    next_date: str,
    category: str = DEFAULT_CATEGORY,
):
    """Adds a new subscription."""
    subs = load_data()
    new_id = 1 if not subs else max(sub.sub_id for sub in subs) + 1
    new_sub = Subscription(new_id, name, cost, cycle, next_date, category)
    subs.append(new_sub)
    save_data(subs)
    print(f"Added subscription: {name}")


def list_subscriptions():
    """Prints all subscriptions in a tabular format."""
    subs = load_data()
    if not subs:
        print("No subscriptions found.")
        return

    print(
        f"{'ID':<5} | {'Name':<20} | {'Cost':<14} | "
        f"{'Cycle':<10} | {'Next Billing':<14} | {'Category'}"
    )
    print("-" * 86)
    for sub in subs:
        print(
            f"{sub.sub_id:<5} | {sub.name:<20} | "
            f"{format_currency(sub.cost, get_currency()):<14} | "
            f"{sub.cycle:<10} | {sub.next_date:<14} | {sub.category}"
        )


def update_subscription(
    sub_id: int,
    name: str = None,
    cost: float = None,
    cycle: str = None,
    next_date: str = None,
    category: str = None,
):
    """Updates an existing subscription; only supplied fields are changed."""
    if all(v is None for v in (name, cost, cycle, next_date, category)):
        print("No fields specified. Use --name, --cost, --cycle, --next_date, or --category.")
        return False

    subs = load_data()
    for sub in subs:
        if sub.sub_id == sub_id:
            if name is not None:
                sub.name = name
            if cost is not None:
                sub.cost = cost
            if cycle is not None:
                sub.cycle = cycle
            if next_date is not None:
                sub.next_date = next_date
            if category is not None:
                sub.category = category
            save_data(subs)
            print(f"Updated subscription ID: {sub_id}")
            return True

    print(f"Subscription ID {sub_id} not found.")
    return False


def delete_subscription(sub_id: int):
    """Deletes a subscription by its ID."""
    subs = load_data()
    initial_len = len(subs)
    subs = [sub for sub in subs if sub.sub_id != sub_id]

    if len(subs) < initial_len:
        save_data(subs)
        print(f"Deleted subscription ID: {sub_id}")
    else:
        print(f"Subscription ID {sub_id} not found.")
