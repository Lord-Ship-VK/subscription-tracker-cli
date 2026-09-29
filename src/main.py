"""
Main entry point for the CLI application.
"""
import argparse
from .manager import add_subscription, list_subscriptions, delete_subscription, update_subscription
from .analytics import show_analytics
from .alerts import check_alerts
from .savings import run_savings_analyzer
from .search import run_search
from .export import run_export
from .utils import validate_date, validate_cost, validate_name, validate_category
from .models import VALID_CATEGORIES, DEFAULT_CATEGORY
from .storage import load_data


def _prompt_validated(prompt, validator, optional=False):
    """Keep prompting for one field until it is valid or optionally blank."""
    while True:
        value = input(prompt)
        if optional and value == "":
            return None
        try:
            return validator(value)
        except ValueError as error:
            print(f"Error: {error}")


def _validate_interactive_cost(value):
    try:
        cost = float(value.strip())
    except ValueError:
        raise ValueError("Cost must be a valid number.")
    return validate_cost(cost)


def _validate_cycle(value):
    cycle = value.strip().lower()
    if cycle not in ("monthly", "yearly"):
        raise ValueError("Billing cycle must be monthly or yearly.")
    return cycle


def _parse_subscription_id(value):
    try:
        sub_id = int(value.strip())
    except ValueError:
        raise ValueError("Subscription ID must be a positive integer.")
    if sub_id <= 0:
        raise ValueError("Subscription ID must be a positive integer.")
    return sub_id


def _prompt_existing_subscription_id(prompt):
    while True:
        sub_id = _prompt_validated(prompt, _parse_subscription_id, optional=True)
        if sub_id is None:
            print("Cancelled.")
            return None
        if any(sub.sub_id == sub_id for sub in load_data()):
            return sub_id
        print(f"Subscription ID {sub_id} not found. Please try again.")


def _interactive_add_subscription():
    """Prompt for a subscription and pass validated values to the manager."""
    name = _prompt_validated("Subscription name: ", validate_name)
    cost = _prompt_validated("Cost: $", _validate_interactive_cost)
    cycle = _prompt_validated("Billing cycle (monthly/yearly): ", _validate_cycle)
    next_date = _prompt_validated(
        "Next renewal date (YYYY-MM-DD): ",
        lambda value: validate_date(value.strip()),
    )
    category = _prompt_validated(
        f"Category ({', '.join(VALID_CATEGORIES)}) [{DEFAULT_CATEGORY}]: ",
        lambda value: validate_category(value.strip() or DEFAULT_CATEGORY),
    )
    add_subscription(name, cost, cycle, next_date, category)


def _interactive_update_subscription():
    """Prompt for changed fields and pass them through existing validation."""
    list_subscriptions()
    sub_id = _prompt_existing_subscription_id(
        "Subscription ID to update (blank to cancel): "
    )
    if sub_id is None:
        return
    print("Leave a field blank to keep its current value.")

    update_subscription(
        sub_id,
        name=_prompt_validated("New name: ", validate_name, optional=True),
        cost=_prompt_validated("New cost: $", _validate_interactive_cost, optional=True),
        cycle=_prompt_validated(
            "New billing cycle (monthly/yearly): ", _validate_cycle, optional=True
        ),
        next_date=_prompt_validated(
            "New renewal date (YYYY-MM-DD): ",
            lambda value: validate_date(value.strip()),
            optional=True,
        ),
        category=_prompt_validated(
            f"New category ({', '.join(VALID_CATEGORIES)}): ",
            validate_category,
            optional=True,
        ),
    )


def _interactive_delete_subscription():
    """Confirm and delete a subscription by ID."""
    list_subscriptions()
    sub_id = _prompt_existing_subscription_id(
        "Subscription ID to delete (blank to cancel): "
    )
    if sub_id is None:
        return
    while True:
        confirmation = input(f"Delete subscription {sub_id}? [y/N]: ").strip().lower()
        if confirmation in ("y", "yes"):
            delete_subscription(sub_id)
            return
        if confirmation in ("", "n", "no"):
            print("Deletion cancelled.")
            return
        print("Please answer yes or no.")


def interactive_menu():
    """Run the terminal application menu until the user exits."""
    actions = {
        "1": _interactive_add_subscription,
        "2": list_subscriptions,
        "3": _interactive_update_subscription,
        "4": _interactive_delete_subscription,
        "5": lambda: run_search(
            term=input("Search name (leave blank to skip): ").strip() or None,
            category=input("Category (leave blank to skip): ").strip() or None,
        ),
        "6": show_analytics,
        "7": check_alerts,
        "8": run_savings_analyzer,
        "9": run_export,
    }

    while True:
        print("\n" + "=" * 48)
        print(" SmartSub | Subscription Expense Tracker")
        print("=" * 48)
        print("  1. Add Subscription")
        print("  2. View Subscriptions")
        print("  3. Update Subscription")
        print("  4. Delete Subscription")
        print("  5. Search Subscriptions")
        print("  6. Spending Analytics")
        print("  7. Renewal Alerts")
        print("  8. Savings Analyzer")
        print("  9. Export Report")
        print("  0. Exit")
        try:
            choice = input("\nSelect an option: ").strip()
            if choice == "0":
                print("Goodbye.")
                return
            action = actions.get(choice)
            if action is None:
                print("Please choose an option from 0 to 9.")
                continue
            action()
        except ValueError as error:
            print(f"Error: {error}")
        except KeyboardInterrupt:
            print("\nCancelled.")
        except EOFError:
            print("\nGoodbye.")
            return


def main():
    """Parses command line arguments and routes to the appropriate function."""
    parser = argparse.ArgumentParser(description="Terminal-based Subscription Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new subscription")
    parser_add.add_argument("name", help="Name of the subscription")
    parser_add.add_argument("cost", type=float, help="Cost of the subscription")
    parser_add.add_argument("cycle", choices=["monthly", "yearly"], help="Billing cycle")
    parser_add.add_argument("next_date", help="Next billing date (YYYY-MM-DD)")
    parser_add.add_argument(
        "--category",
        choices=VALID_CATEGORIES,
        default=DEFAULT_CATEGORY,
        help=f"Category (default: {DEFAULT_CATEGORY})",
    )

    # Update command
    parser_update = subparsers.add_parser("update", help="Update an existing subscription")
    parser_update.add_argument("id", type=int, help="ID of the subscription to update")
    parser_update.add_argument("--name", help="New name of the subscription")
    parser_update.add_argument("--cost", type=float, help="New cost of the subscription")
    parser_update.add_argument("--cycle", choices=["monthly", "yearly"], help="New billing cycle")
    parser_update.add_argument("--next_date", help="New billing date (YYYY-MM-DD)")
    parser_update.add_argument(
        "--category",
        choices=VALID_CATEGORIES,
        help="New category",
    )

    # List command
    subparsers.add_parser("list", help="List all subscriptions")

    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a subscription by ID")
    parser_delete.add_argument("id", type=int, help="ID of the subscription to delete")

    # Analytics command
    subparsers.add_parser("analytics", help="Show expense analytics")

    # Alerts command
    subparsers.add_parser("alerts", help="Check for upcoming renewals")

    # Savings command
    subparsers.add_parser("savings", help="Interactively calculate potential savings from cancellations")

    # Search command
    parser_search = subparsers.add_parser("search", help="Search and filter subscriptions")
    parser_search.add_argument("term", nargs="?", default=None,
                               help="Search term (matches subscription name, case-insensitive)")
    parser_search.add_argument("--category", default=None,
                               help="Filter by category")

    # Export command
    subparsers.add_parser("export", help="Export subscription data to a CSV report")

    args = parser.parse_args()

    if args.command is None:
        interactive_menu()

    elif args.command == "add":
        try:
            name = validate_name(args.name)
            cost = validate_cost(args.cost)
            next_date = validate_date(args.next_date)
            category = validate_category(args.category)
            add_subscription(name, cost, args.cycle, next_date, category)
        except ValueError as e:
            print(f"Error: {e}")

    elif args.command == "update":
        try:
            name = validate_name(args.name) if args.name is not None else None
            cost = validate_cost(args.cost) if args.cost is not None else None
            next_date = validate_date(args.next_date) if args.next_date is not None else None
            category = validate_category(args.category) if args.category is not None else None
            update_subscription(args.id, name=name, cost=cost, cycle=args.cycle,
                                next_date=next_date, category=category)
        except ValueError as e:
            print(f"Error: {e}")

    elif args.command == "list":
        list_subscriptions()

    elif args.command == "delete":
        delete_subscription(args.id)

    elif args.command == "analytics":
        show_analytics()

    elif args.command == "alerts":
        check_alerts()

    elif args.command == "savings":
        run_savings_analyzer()

    elif args.command == "search":
        run_search(term=args.term, category=args.category)

    elif args.command == "export":
        run_export()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
