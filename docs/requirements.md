# SmartSub: Requirements

## Functional Requirements

The system must provide a command-line interface supporting the following core operations:

### 1. Add Subscription
- **Input**: Name (string), Cost (positive float), Cycle (monthly/yearly), Next Renewal Date (YYYY-MM-DD), Category (optional, restricted set).
- **Process**: Assigns a unique integer ID. Validates all inputs. Calculates the correct initial state. Appends to the internal data structure. Saves to disk.
- **Output**: Success message confirming the addition.

### 2. List Subscriptions
- **Input**: None.
- **Process**: Retrieves all stored subscriptions from local storage. Formats them into a padded, readable ASCII table.
- **Output**: Tabular display of ID, Name, Cost, Cycle, Next Billing Date, and Category.

### 3. Update Subscription
- **Input**: Subscription ID (integer) and one or more optional fields (name, cost, cycle, next_date, category).
- **Process**: Locates the subscription by ID. Updates only the provided fields. Saves changes to disk. Rejects the operation if no fields are provided.
- **Output**: Success message or a "not found" / "no fields specified" error.

### 4. Delete Subscription
- **Input**: Subscription ID (integer).
- **Process**: Locates and removes the corresponding subscription from the data list. Saves changes to disk.
- **Output**: Success message confirming deletion or "not found" error.

### 5. Expense Analytics
- **Input**: None.
- **Process**: Calculates the normalized monthly and yearly equivalent cost for all subscriptions. Groups spending by category. Identifies the single most expensive subscription based on its monthly equivalent cost.
- **Output**: Formatted analytics report displaying total count, total monthly cost, total yearly cost, per-category breakdown, and the highest individual expense.

### 6. Renewal Alerts
- **Input**: None.
- **Process**: Compares all subscription renewal dates against the current system date. Filters for dates within a 0 to 7-day future window.
- **Output**: Warning messages highlighting which subscriptions are due for payment and their exact cost.

### 7. Savings Analyzer
- **Input**: A comma-separated string of subscription IDs (entered interactively).
- **Process**: Validates the input string. Looks up the corresponding subscriptions. Calculates the total monthly and yearly equivalent cost of only those selected subscriptions. Does not delete any data.
- **Output**: A hypothetical savings report detailing exactly how much money would be saved by cancelling the selected services.

### 8. Search & Filter
- **Input**: Optional partial search term (string) and/or optional exact category (string).
- **Process**: Performs a case-insensitive substring match on subscription names and an exact case-insensitive match on the category. Applies AND logic if both are provided.
- **Output**: Tabular list of matching subscriptions and a count of total matches.

### 9. CSV Export
- **Input**: None (uses a default internal path `reports/subscription_report.csv`).
- **Process**: Formats all data into CSV rows. Calculates the monthly and yearly equivalent costs for each row. Creates parent directories if missing.
- **Output**: A CSV file written to disk and a terminal summary of what was exported.

## Non-Functional Requirements

- **Dependency-Free**: The application must run using only the Python Standard Library. No external packages (like Pandas or Requests) are permitted.
- **Data Persistence**: Data must persist between application runs.
- **Data Format**: Storage must utilize plain text JSON to remain human-readable and easily auditable.
- **Modularity**: Code must be separated into distinct modules based on responsibility (e.g., storage, UI, business logic, math).
- **Testability**: Core business logic (like savings calculations and date math) must be implemented as pure functions to facilitate unit testing without disk I/O.

## Validation and Error Handling

The application must handle bad data gracefully without crashing:
- **Cost**: Must be a positive numeric value.
- **Name**: Cannot be an empty string.
- **Dates**: Must strictly match the `YYYY-MM-DD` ISO format. Invalid dates must be rejected.
- **Categories**: Must exactly match one of the predefined system categories (Entertainment, Education, Productivity, Cloud Storage, Software, Other). Unknown categories must be rejected.
- **File I/O**: If the JSON file is missing, the system must treat it as an empty database and create the file upon the first save. If the JSON is completely corrupted, it should handle the error safely.
- **Invalid IDs**: Providing an ID that does not exist to update, delete, or analyze must print a user-friendly error message, not a Python traceback.
