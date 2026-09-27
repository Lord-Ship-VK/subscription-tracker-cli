"""
Handles data persistence.

load_data() automatically advances any stale renewal dates and persists the
updated values back to disk before returning the subscription list.  This
means every command in the application always works with current dates without
any additional wiring.
"""
import json
import os
from .models import Subscription
from .utils import refresh_renewal_dates

# Determine the absolute path to the data folder based on this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "data", "subscriptions.json")

# Allow overriding for tests
DATA_FILE = DEFAULT_DATA_FILE


def set_data_file(path: str):
    """Set the data file path (useful for testing)."""
    global DATA_FILE
    DATA_FILE = path


def load_data() -> list:
    """
    Load subscriptions from the JSON file.

    After deserialising, any subscription whose ``next_date`` is in the past
    is automatically advanced to the next valid billing date via
    ``refresh_renewal_dates()``.  If any dates were updated the corrected
    data is written back to disk before the list is returned, so the stored
    JSON stays current.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            subscriptions = [Subscription.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError):
        return []

    # Auto-advance stale renewal dates and persist only if something changed.
    if refresh_renewal_dates(subscriptions):
        save_data(subscriptions)

    return subscriptions


def save_data(subscriptions: list):
    """Save subscriptions to the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump([sub.to_dict() for sub in subscriptions], f, indent=4)
