"""
Models for the subscription tracker.
"""
from typing import Dict, Any

VALID_CATEGORIES = [
    "Entertainment",
    "Education",
    "Productivity",
    "Cloud Storage",
    "Software",
    "Other",
]

DEFAULT_CATEGORY = "Other"


class Subscription:
    """Represents a single subscription."""

    def __init__(
        self,
        sub_id: int,
        name: str,
        cost: float,
        cycle: str,
        next_date: str,
        category: str = DEFAULT_CATEGORY,
    ):
        self.sub_id = sub_id
        self.name = name
        self.cost = cost
        self.cycle = cycle
        self.next_date = next_date
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        """Converts the subscription to a dictionary for JSON serialization."""
        return {
            "id": self.sub_id,
            "name": self.name,
            "cost": self.cost,
            "cycle": self.cycle,
            "next_date": self.next_date,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """
        Creates a Subscription instance from a dictionary.

        The 'category' key is optional so that existing records stored without
        a category are still loaded successfully, defaulting to 'Other'.
        """
        return cls(
            sub_id=data.get('id', 0),
            name=data.get('name', ''),
            cost=data.get('cost', 0.0),
            cycle=data.get('cycle', ''),
            next_date=data.get('next_date', ''),
            category=data.get('category', DEFAULT_CATEGORY),
        )

