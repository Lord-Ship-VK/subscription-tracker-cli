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

    if args.command == "add":
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
