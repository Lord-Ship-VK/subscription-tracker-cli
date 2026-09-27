# SmartSub: Storage Design

## JSON Storage

SmartSub uses human-readable JSON for data persistence. By strictly isolating disk I/O in the `storage.py` module, the application ensures that data format changes or underlying storage swaps (e.g., to a database in the future) would not affect the business logic or calculations.

## Runtime Data Location

By default, the data file is stored relative to the project root at:
`data/subscriptions.json`

The global `DATA_FILE` constant in `src/storage.py` determines this location. It can be overridden for testing via the `set_data_file(path)` function, allowing unit tests to use isolated, ephemeral temp files.

## Subscription Record Fields

Each record maps directly to the `Subscription` class defined in `models.py`.

- `id`: Unique integer. Incremented automatically by `max(ids) + 1`. Note that IDs can be reused if the highest ID is deleted.
- `name`: String. Cannot be empty.
- `cost`: Float. Must be positive.
- `cycle`: String. Restricted to `"monthly"` or `"yearly"`.
- `next_date`: String. Iso-formatted date `"YYYY-MM-DD"`.
- `category`: String. Defaults to `"Other"`. Backward compatible with older records missing this field.

## Example JSON Record

```json
[
  {
    "id": 1,
    "name": "Netflix Premium",
    "cost": 19.99,
    "cycle": "monthly",
    "next_date": "2026-10-15",
    "category": "Entertainment"
  },
  {
    "id": 2,
    "name": "GitHub Pro",
    "cost": 48.00,
    "cycle": "yearly",
    "next_date": "2026-11-01",
    "category": "Software"
  }
]
```

## Load/Save Process

### `load_data()`
1. Checks if the file exists. If not, returns `[]`.
2. Reads and parses the JSON file. If the file is empty or corrupted (e.g. `json.JSONDecodeError`), it catches the error and returns `[]`.
3. Maps each dictionary back into a `Subscription` object using `Subscription.from_dict()`.
4. Passes the list of objects to `refresh_renewal_dates()`.
5. If the refresh process detects and advances any past dates, `load_data()` immediately calls `save_data()` to persist the updated dates.
6. Returns the list of objects.

### `save_data(subs)`
1. Converts the list of `Subscription` objects into a list of dictionaries using `sub.to_dict()`.
2. Identifies the directory path of the target `DATA_FILE`.
3. Creates any missing parent directories (`os.makedirs`).
4. Writes the JSON list to the file with an indentation of 4 spaces for readability.

## Missing File / Empty Data Behavior

If `data/subscriptions.json` is missing (e.g., on a fresh clone), `load_data()` will silently return an empty list. The file will be created dynamically inside the `data/` folder the first time `save_data()` is triggered (usually during the first `add` operation).

## Corrupt JSON Behavior

If the file exists but contains invalid JSON (or non-list JSON), `load_data()` catches `json.JSONDecodeError` and `KeyError` and silently returns an empty list `[]`. It prioritizes not crashing, though returning an empty list means any subsequent saves will overwrite the corrupted file with a fresh, valid array.

## Renewal-Date Refresh Behavior

Because there is no background daemon running continuously, dates are refreshed lazily. Every time the user executes a command that requires reading data (like `list`, `search`, or `analytics`), `load_data()` checks the system clock. If it finds a `next_date` that is in the past, it advances it forward month-by-month or year-by-year until it reaches the future, and saves the file back to disk. This ensures all analytics and alerts are based on correct, current data.
