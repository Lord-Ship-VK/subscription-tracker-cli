"""
Export subscription data to a CSV report.

``generate_report()`` is the pure logic: it takes a list of subscriptions
and a file path, writes the CSV, and returns a summary dict.
``run_export()`` owns I/O: loading data, calling the generator, and printing
a terminal summary.
"""
import csv
import os
from .storage import load_data, get_currency, get_user_id
from .analytics import monthly_cost
from .utils import format_currency


# Default output path, relative to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPORT_PATH = os.path.join(BASE_DIR, "reports", "subscription_report.csv")

CSV_HEADERS = [
    "ID",
    "Name",
    "Cost",
    "Cycle",
    "Category",
    "Next Renewal Date",
    "Monthly Equivalent",
    "Yearly Equivalent",
    "Currency",
]


def generate_report(subscriptions: list, output_path: str, currency: str = "USD") -> dict:
    """
    Write subscription data to a CSV file and return a summary dict.

    Parameters
    ----------
    subscriptions : list of Subscription objects.
    output_path   : absolute path where the CSV will be created.  Parent
                    directories are created automatically.

    Returns
    -------
    dict with keys ``path``, ``total``, ``monthly``, ``yearly``.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    monthly_total = 0.0
    yearly_total = 0.0

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for sub in subscriptions:
            monthly = monthly_cost(sub)
            yearly = monthly * 12
            monthly_total += monthly
            yearly_total += yearly

            writer.writerow([
                sub.sub_id,
                sub.name,
                f"{sub.cost:.2f}",
                sub.cycle,
                sub.category,
                sub.next_date,
                f"{monthly:.2f}",
                f"{yearly:.2f}",
                currency,
            ])

    return {
        "path": output_path,
        "total": len(subscriptions),
        "monthly": monthly_total,
        "yearly": yearly_total,
    }


def run_export(output_path: str = None):
    """
    Load subscriptions, generate the CSV report, and print a terminal summary.

    Called by the CLI ``export`` subcommand.
    """
    if output_path is None:
        output_path = os.path.join(
            BASE_DIR, "reports", get_user_id(), "subscription_report.csv"
        )

    subs = load_data()

    if not subs:
        print("No subscriptions found. Nothing to export.")
        return

    currency = get_currency()
    summary = generate_report(subs, output_path, currency)

    print("--- Export Report ---")
    print(f"File created:          {summary['path']}")
    print(f"Total Subscriptions:   {summary['total']}")
    print(
        f"Total Monthly Cost:    {format_currency(summary['monthly'], currency)}"
    )
    print(
        f"Total Yearly Cost:     {format_currency(summary['yearly'], currency)}"
    )
