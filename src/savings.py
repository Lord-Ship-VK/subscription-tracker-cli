"""
Savings Analyzer — calculates hypothetical savings from cancelling subscriptions.

Design
------
``calculate_savings`` is a pure function: it takes a list of Subscription
objects and a raw ID-input string, validates them, and returns a result
dictionary.  It never reads from disk or prints anything, which makes it
straightforward to unit-test.

``run_savings_analyzer`` owns all I/O: it loads data, displays the
subscription list, prompts the user, calls ``calculate_savings``, and
prints the final report.
"""
from .storage import load_data
from .analytics import monthly_cost


# ---------------------------------------------------------------------------
# Pure calculation layer (testable without disk or stdout)
# ---------------------------------------------------------------------------

def calculate_savings(subscriptions: list, ids_input: str) -> dict:
    """
    Parse ``ids_input``, validate it against ``subscriptions``, and return a
    result dictionary with the following keys:

    ``selected``     – list of matched Subscription objects  
    ``monthly``      – total monthly savings (float)  
    ``yearly``       – total yearly savings  == monthly * 12 (float)  
    ``errors``       – list of human-readable error strings (empty on success)

    No subscriptions are deleted; this is a read-only hypothetical.
    """
    result = {
        "selected": [],
        "monthly": 0.0,
        "yearly": 0.0,
        "errors": [],
    }

    # --- parse the raw input string ---
    if not ids_input or not ids_input.strip():
        result["errors"].append("No IDs entered. Please enter at least one subscription ID.")
        return result

    raw_tokens = ids_input.strip().split(",")
    parsed_ids = []
    for token in raw_tokens:
        token = token.strip()
        if not token:
            continue
        try:
            parsed_ids.append(int(token))
        except ValueError:
            result["errors"].append(
                f"'{token}' is not a valid integer ID."
            )

    if result["errors"]:
        return result

    if not parsed_ids:
        result["errors"].append("No IDs entered. Please enter at least one subscription ID.")
        return result

    # --- look up each ID ---
    sub_map = {sub.sub_id: sub for sub in subscriptions}
    found = []
    for sid in parsed_ids:
        if sid not in sub_map:
            result["errors"].append(f"ID {sid} does not exist.")
        else:
            found.append(sub_map[sid])

    if result["errors"]:
        return result

    # --- calculate savings ---
    monthly_savings = sum(monthly_cost(sub) for sub in found)
    result["selected"] = found
    result["monthly"] = monthly_savings
    result["yearly"] = monthly_savings * 12
    return result


# ---------------------------------------------------------------------------
# Interactive I/O layer
# ---------------------------------------------------------------------------

def run_savings_analyzer():
    """
    Interactive savings analyzer.

    1. Loads the current subscriptions from disk.
    2. Displays the full subscription list with IDs.
    3. Prompts the user for a comma-separated list of IDs to consider cancelling.
    4. Calls ``calculate_savings`` and prints the hypothetical savings report.

    Subscriptions are never modified or deleted.
    """
    subs = load_data()

    if not subs:
        print("--- Savings Analyzer ---")
        print("No subscriptions found. Add some subscriptions first.")
        return

    # Display current subscriptions
    print("--- Savings Analyzer ---")
    print("Your current subscriptions:\n")
    print(f"  {'ID':<5} {'Name':<22} {'Cost':<12} {'Cycle':<10} {'Category'}")
    print("  " + "-" * 65)
    for sub in subs:
        cost_str = f"${sub.cost:.2f}/{sub.cycle[:2]}"
        print(f"  {sub.sub_id:<5} {sub.name:<22} {cost_str:<12} {sub.cycle:<10} {sub.category}")

    print()
    print("Enter the IDs of subscriptions you are considering cancelling,")
    print("separated by commas (e.g.  1, 3, 5):")
    print()

    while True:
        try:
            ids_input = input("  IDs > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        result = calculate_savings(subs, ids_input)

        if not result["errors"]:
            break

        print()
        for err in result["errors"]:
            print(f"  Error: {err}")
        print("Please try again.")

    # Print savings report
    print()
    print("--- Hypothetical Savings Report ---")
    print()
    print("  Subscriptions considered for cancellation:")
    for sub in result["selected"]:
        monthly = monthly_cost(sub)
        print(f"    [{sub.sub_id}] {sub.name:<22} ${monthly:.2f}/month")

    print()
    print(f"  Potential Monthly Savings:  ${result['monthly']:.2f}")
    print(f"  Potential Yearly Savings:   ${result['yearly']:.2f}")
    print()
    print("  Note: No subscriptions have been cancelled.")
