# SmartSub: Workflows

This document outlines the step-by-step workflow for every major CLI command.

## Mermaid Flowcharts

### 1. Add Workflow

```mermaid
sequenceDiagram
    participant CLI as main.py
    participant Val as utils.py
    participant Mgr as manager.py
    participant Store as storage.py
    participant Disk as JSON

    CLI->>Val: validate_cost(), validate_date(), etc.
    Val-->>CLI: Validated Data
    CLI->>Mgr: add_subscription(name, cost, cycle, date, category)
    Mgr->>Store: load_data()
    Store->>Disk: Read JSON
    Disk-->>Store: 
    Store-->>Mgr: List of Subscriptions
    Mgr->>Mgr: Calculate new ID (max + 1)
    Mgr->>Mgr: Append new Subscription
    Mgr->>Store: save_data(subs)
    Store->>Disk: Write JSON
    Mgr-->>CLI: Print success
```

### 2. Update Workflow

```mermaid
sequenceDiagram
    participant CLI as main.py
    participant Mgr as manager.py
    participant Store as storage.py

    CLI->>Mgr: update_subscription(id, kwargs...)
    Mgr->>Mgr: Check if any kwargs provided
    alt No fields provided
        Mgr-->>CLI: Return error message
    else Fields provided
        Mgr->>Store: load_data()
        Store-->>Mgr: List of Subscriptions
        Mgr->>Mgr: Find sub by ID
        alt ID Found
            Mgr->>Mgr: Apply new values
            Mgr->>Store: save_data(subs)
            Mgr-->>CLI: Print success
        else ID Not Found
            Mgr-->>CLI: Print error
        end
    end
```

### 3. Analytics Workflow

```mermaid
sequenceDiagram
    participant CLI as main.py
    participant Analytics as analytics.py
    participant Store as storage.py

    CLI->>Analytics: show_analytics()
    Analytics->>Store: load_data()
    Store-->>Analytics: List of Subscriptions
    loop Every Subscription
        Analytics->>Analytics: monthly_cost()
        Analytics->>Analytics: Accumulate by category
        Analytics->>Analytics: Check if most expensive
    end
    Analytics-->>CLI: Print formatted report
```

### 4. Savings Workflow

```mermaid
sequenceDiagram
    participant CLI as main.py
    participant SavIO as savings.py (I/O)
    participant SavCalc as savings.py (Pure)
    participant Store as storage.py

    CLI->>SavIO: run_savings_analyzer()
    SavIO->>Store: load_data()
    Store-->>SavIO: List of Subscriptions
    SavIO-->>User: Print all subs, prompt for IDs
    User-->>SavIO: "1, 3"
    SavIO->>SavCalc: calculate_savings(subs, "1, 3")
    SavCalc->>SavCalc: Parse & Validate IDs
    SavCalc->>SavCalc: Calculate sums (using monthly_cost)
    SavCalc-->>SavIO: Result Dictionary
    SavIO-->>CLI: Print Hypothetical Report
```

## Detailed Text Workflows

### List Workflow
1. User calls `python3 -m src.main list`.
2. `main.py` calls `manager.list_subscriptions()`.
3. `manager.py` calls `storage.load_data()`.
4. `storage.py` parses the JSON file, refreshes any stale renewal dates, and returns the data.
5. `manager.py` loops through the list and prints a formatted ASCII table.

### Delete Workflow
1. User calls `python3 -m src.main delete <id>`.
2. `main.py` calls `manager.delete_subscription(id)`.
3. `manager.py` loads data, filters the list to remove the matching ID, and saves the new list to disk. Prints success or failure.

### Renewal/Alert Workflow
1. User calls `python3 -m src.main alerts`.
2. `main.py` calls `alerts.check_alerts()`.
3. `alerts.py` loads data (which inherently auto-advances any dates already in the past).
4. `alerts.py` compares the current date to every subscription's `next_date`.
5. If the difference is between 0 and 7 days, it is printed as an alert.

### Search Workflow
1. User calls `python3 -m src.main search <term> --category <cat>`.
2. `main.py` calls `search.run_search(term, category)`.
3. `search.py` loads data and passes it to the pure `filter_subscriptions()` function.
4. The pure function applies case-insensitive substring matching and returns a new list.
5. `search.py` prints the results as a table.

### Export Workflow
1. User calls `python3 -m src.main export`.
2. `main.py` calls `export.run_export()`.
3. `export.py` loads data, passes it to the pure `generate_report()` function.
4. The generator creates the `reports/` directory if needed, calculates equivalent costs, writes the CSV, and returns a summary object.
5. The wrapper prints the summary to the terminal.
