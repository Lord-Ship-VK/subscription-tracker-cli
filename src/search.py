"""
Search and filter subscriptions by name and/or category.

The filtering logic lives in ``filter_subscriptions()`` — a pure function
that takes an already-loaded list of Subscription objects and returns a
filtered list.  ``run_search()`` owns the I/O: loading data, calling the
filter, and printing results.
"""
from .storage import load_data


def filter_subscriptions(subscriptions: list,
                         term: str = None,
                         category: str = None) -> list:
    """
    Return subscriptions matching the given filters.

    Parameters
    ----------
    subscriptions : list of Subscription objects to search.
    term          : optional search string matched case-insensitively against
                    the subscription name (partial match).
    category      : optional category string matched case-insensitively
                    (exact match against the category field).

    Returns
    -------
    A new list containing only the subscriptions that satisfy **all**
    supplied filters.  If neither filter is given, all subscriptions are
    returned.
    """
    results = subscriptions

    if term is not None:
        lower_term = term.lower()
        results = [s for s in results if lower_term in s.name.lower()]

    if category is not None:
        lower_cat = category.lower()
        results = [s for s in results if s.category.lower() == lower_cat]

    return results


def run_search(term: str = None, category: str = None):
    """
    Load all subscriptions, apply filters, and print matching results.

    Called by the CLI ``search`` subcommand.
    """
    subs = load_data()

    if not subs:
        print("No subscriptions found.")
        return

    results = filter_subscriptions(subs, term=term, category=category)

    if not results:
        parts = []
        if term:
            parts.append(f"name matching '{term}'")
        if category:
            parts.append(f"category '{category}'")
        criteria = " and ".join(parts) if parts else "the given criteria"
        print(f"No subscriptions found matching {criteria}.")
        return

    print(
        f"{'ID':<5} | {'Name':<20} | {'Cost':<10} | "
        f"{'Cycle':<10} | {'Next Billing':<14} | {'Category'}"
    )
    print("-" * 82)
    for sub in results:
        print(
            f"{sub.sub_id:<5} | {sub.name:<20} | ${sub.cost:<9.2f} | "
            f"{sub.cycle:<10} | {sub.next_date:<14} | {sub.category}"
        )
    print(f"\n{len(results)} result(s) found.")
