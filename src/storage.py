"""
Handles data persistence.

load_data() automatically advances any stale renewal dates and persists the
updated values back to disk before returning the subscription list.  This
means every command in the application always works with current dates without
any additional wiring.
"""
import json
import os
import re
import shutil
from .models import Subscription
from .utils import refresh_renewal_dates

# Determine the absolute path to the data folder based on this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "data", "subscriptions.json")
DEFAULT_USER_DATA_DIR = os.path.join(BASE_DIR, "data", "users")

# Allow overriding for tests
DATA_FILE = DEFAULT_DATA_FILE
USER_DATA_DIR = DEFAULT_USER_DATA_DIR
ACTIVE_USER_ID = "default"
_DATA_FILE_OVERRIDE = False


def validate_user_id(user_id: str) -> str:
    """Return a safe user ID suitable for use as a local directory name."""
    if not isinstance(user_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}", user_id):
        raise ValueError("User ID must be 1-32 characters using letters, numbers, '_' or '-'.")
    return user_id


def set_user_id(user_id: str):
    """Select the user whose local data and preferences are active."""
    global ACTIVE_USER_ID, DATA_FILE
    ACTIVE_USER_ID = validate_user_id(user_id)
    if _DATA_FILE_OVERRIDE:
        return

    DATA_FILE = os.path.join(USER_DATA_DIR, ACTIVE_USER_ID, "subscriptions.json")
    if (
        ACTIVE_USER_ID == "default"
        and not os.path.exists(DATA_FILE)
        and os.path.exists(DEFAULT_DATA_FILE)
    ):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        shutil.copy2(DEFAULT_DATA_FILE, DATA_FILE)


def set_user_data_dir(path: str):
    """Set the user-data root directory (useful for testing)."""
    global USER_DATA_DIR, DATA_FILE
    USER_DATA_DIR = path
    if not _DATA_FILE_OVERRIDE:
        DATA_FILE = os.path.join(USER_DATA_DIR, ACTIVE_USER_ID, "subscriptions.json")


def set_data_file(path: str):
    """Set the data file path (useful for testing)."""
    global DATA_FILE, _DATA_FILE_OVERRIDE
    _DATA_FILE_OVERRIDE = path is not None
    DATA_FILE = path or os.path.join(USER_DATA_DIR, ACTIVE_USER_ID, "subscriptions.json")


def _profile_file() -> str:
    return os.path.join(USER_DATA_DIR, ACTIVE_USER_ID, "profile.json")


def get_currency() -> str:
    """Return the active user's currency, defaulting to US dollars."""
    try:
        with open(_profile_file(), 'r') as profile:
            currency = json.load(profile).get("currency", "USD")
    except (OSError, json.JSONDecodeError, AttributeError):
        return "USD"
    return currency if currency in ("USD", "INR") else "USD"


def get_user_id() -> str:
    """Return the currently selected user ID."""
    return ACTIVE_USER_ID


def set_currency(currency: str):
    """Persist the active user's display currency (no exchange conversion)."""
    if not isinstance(currency, str):
        raise ValueError("Currency must be USD or INR.")
    currency = currency.upper()
    if currency not in ("USD", "INR"):
        raise ValueError("Currency must be USD or INR.")
    profile_file = _profile_file()
    os.makedirs(os.path.dirname(profile_file), exist_ok=True)
    with open(profile_file, 'w') as profile:
        json.dump({"currency": currency}, profile, indent=4)


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
