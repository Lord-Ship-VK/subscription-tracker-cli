# SmartSub — Subscription Expense Tracker & Analyzer

SmartSub is a terminal-based Python application for organizing recurring subscriptions, tracking renewal dates, and understanding monthly and yearly spending. It is useful for anyone managing multiple services, stores subscription data locally as JSON, and has no external dependencies. Built as a Python Essentials academic project, it uses focused modules and includes a `unittest` suite.

## Why SmartSub?

When recurring services are spread across different providers, it is easy to lose track of their costs, renewal dates, and categories. SmartSub brings those details together and helps users review spending or estimate potential savings before deciding what to cancel.

## Key Features

| Feature | Description |
|---|---|
| Subscription management | Add, view, update, and delete subscriptions. |
| Categories | Organize subscriptions using six predefined categories. |
| Spending analytics | Review subscription count, monthly and yearly totals, category spending, and the subscription with the highest monthly-equivalent cost. |
| Renewal alerts | See subscriptions renewing within the next seven days. |
| Renewal-date handling | Advance past renewal dates automatically, including month-end and leap-year clamping. |
| Savings analyzer | Estimate monthly and yearly savings for selected subscriptions without deleting them. |
| Search and filter | Search names by partial match and filter by exact category. |
| CSV export | Export subscription and monthly/yearly equivalent costs to CSV. |
| User profiles | Keep subscription data and currency preferences separate by local user ID. |
| Currency display | Display costs in USD or INR without converting the stored amounts. |

The predefined categories are Entertainment, Education, Productivity, Cloud Storage, Software, and Other. New subscriptions default to Other when no category is specified.

## Technologies

- Python and its standard library
- JSON for local data storage
- CSV for report generation
- `unittest` for tests
- `argparse` for command-line options

## Quick Start

### Prerequisites

- Python 3.6 or newer
- Git, or a browser to download the repository as a ZIP

SmartSub uses only Python standard-library modules. No additional packages or pip installation are required.

### 1. Clone the repository

```bash
git clone https://github.com/Lord-Ship-VK/subscription-tracker-cli.git
```

### 2. Enter the project directory

```bash
cd subscription-tracker-cli
```

Alternatively, download and extract the ZIP from the [GitHub repository](https://github.com/Lord-Ship-VK/subscription-tracker-cli), then open a terminal in the extracted directory.

### 3. Verify Python

```bash
python3 --version
```

### 4. Run SmartSub

```bash
python3 -m src.main
```

Running without a subcommand asks for a user ID unless `--user-id` is provided, then opens the interactive menu. The menu includes:

```text
SmartSub | User: <user-id> | Currency: <currency>
1. Add Subscription
2. View Subscriptions
3. Update Subscription
4. Delete Subscription
5. Search Subscriptions
6. Spending Analytics
7. Renewal Alerts
8. Savings Analyzer
9. Export Report
10. Set Currency
0. Exit
```

On Windows, use the Python launcher:

```powershell
py --version
py -m src.main
```

To run the test suite, use:

```bash
python3 -m unittest discover tests -v
```

On Windows, the equivalent command is `py -m unittest discover tests -v`.

## Command-Line Usage

Run commands from the project root using `python3 -m src.main <command> [arguments]`. Running without a command starts the interactive menu.

| Command | Purpose |
|---|---|
| `add NAME COST CYCLE YYYY-MM-DD [--category CATEGORY]` | Add a subscription. `CYCLE` is `monthly` or `yearly`; category defaults to `Other`. |
| `list` | List subscriptions in a table. |
| `update ID [options]` | Update only the supplied fields: `--name`, `--cost`, `--cycle`, `--next_date`, or `--category`. |
| `delete ID` | Delete a subscription by ID. |
| `search [TERM] [--category CATEGORY]` | Search names by partial, case-insensitive match and/or filter by category. Both filters are combined. |
| `analytics` | Show totals, category spending, and the most expensive subscription. |
| `alerts` | Check for renewals in the next seven days. |
| `savings` | Interactively estimate savings for comma-separated subscription IDs. |
| `export` | Write a CSV report for the selected user. |
| `currency [CURRENCY]` | Show or set the display currency (`USD` or `INR`). |

Examples:

```bash
python3 -m src.main add "Netflix Premium" 19.99 monthly 2026-10-15 --category Entertainment
python3 -m src.main update 1 --cost 22.99 --category Entertainment
python3 -m src.main search "net"
python3 -m src.main search --category Software
python3 -m src.main --user-id alice add "Netflix" 19.99 monthly 2026-10-15
python3 -m src.main list --user-id alice
python3 -m src.main --user-id alice currency INR
```

The `--user-id` option can appear before or after a subcommand. Without it, command-line operations use the `default` profile. User IDs must be 1-32 characters and contain only letters, numbers, underscores, or hyphens. Interactive add and update flows also allow changing currency before entering a cost.

Currency changes display formatting only; costs are not exchange-converted. USD is the default and displays with `$`; INR displays with the `INR` prefix. Currency preferences are stored separately for each user.

## Data and Behavior

- Subscription data is stored in `data/users/<user-id>/subscriptions.json`; each profile's currency preference is stored in `profile.json` in the same directory.
- On first use of the `default` profile, the original `data/subscriptions.json` is copied into that profile if it exists. The original file is not deleted.
- When data is loaded, past renewal dates are advanced by their billing cycle and saved. Monthly dates clamp to the last valid day of shorter months; yearly dates handle leap days.
- CSV exports are written to `reports/<user-id>/subscription_report.csv` and include the selected currency and monthly/yearly cost equivalents.
- Input validation checks non-empty names, positive finite costs, `YYYY-MM-DD` dates, monthly or yearly billing cycles, predefined categories, and user IDs. ID-based operations report when a subscription cannot be found.

## Project Structure

```text
subscription-tracker-cli/
├── data/
│   ├── subscriptions.json       # Legacy data used to initialize the default profile
│   └── users/                   # Per-user data and preferences (created at runtime)
├── docs/
│   ├── architecture.md
│   ├── problem-statement.md
│   ├── requirements.md
│   ├── storage-design.md
│   ├── uml.md
│   └── workflow.md
├── reports/
│   ├── subscription_report.csv  # Existing report
│   └── <user-id>/               # Per-user export output
├── src/
│   ├── __init__.py
│   ├── alerts.py                 # Renewal alerts
│   ├── analytics.py              # Spending analytics
│   ├── export.py                 # CSV report generation
│   ├── main.py                   # CLI and interactive menu
│   ├── manager.py                # Subscription operations
│   ├── models.py                 # Subscription model and categories
│   ├── savings.py                # Savings analyzer
│   ├── search.py                 # Search and filtering
│   ├── storage.py                # JSON persistence and user profiles
│   └── utils.py                  # Validation and date arithmetic
├── tests/
│   ├── __init__.py
│   └── test_tracker.py           # Unit tests
├── .gitignore
└── README.md
```

## Known Limitations

- If the subscription with the highest ID is deleted, the next added subscription reuses that ID.
- A monthly renewal on the 31st clamps to February's last day (the 28th or 29th). Later renewal dates advance from the clamped date.
- Currency selection changes display formatting only; it does not convert amounts between USD and INR.

## Future Enhancements

Potential future ideas, not currently implemented:

- Live exchange-rate conversion
- Cloud synchronization with a remote database
- Weekly or quarterly billing cycles
- A graphical or web-based frontend
