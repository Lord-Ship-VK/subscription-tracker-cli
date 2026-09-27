import unittest
import os
import tempfile
import sys
import io
import json
from datetime import date
from src import storage, manager, analytics, alerts, utils

class TestSubscriptionTracker(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for tests to isolate from real data
        self.fd, self.temp_file = tempfile.mkstemp(suffix='.json')
        storage.set_data_file(self.temp_file)
        
        # Ensure it starts empty
        with open(self.temp_file, 'w') as f:
            f.write("[]")

    def tearDown(self):
        os.close(self.fd)
        os.remove(self.temp_file)

    def test_add_subscription(self):
        manager.add_subscription("Test", 10.0, "monthly", "2026-10-01")
        data = storage.load_data()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].name, "Test")
        self.assertEqual(data[0].cost, 10.0)

    def test_update_subscription(self):
        manager.add_subscription("Test", 10.0, "monthly", "2026-10-01")
        data = storage.load_data()
        sub_id = data[0].sub_id
        
        # Update cost and name
        manager.update_subscription(sub_id, name="Test Updated", cost=20.0)
        data = storage.load_data()
        self.assertEqual(data[0].name, "Test Updated")
        self.assertEqual(data[0].cost, 20.0)
        self.assertEqual(data[0].cycle, "monthly") # Cycle should remain unchanged

    def test_delete_subscription(self):
        manager.add_subscription("Test", 10.0, "monthly", "2026-10-01")
        data = storage.load_data()
        sub_id = data[0].sub_id
        
        manager.delete_subscription(sub_id)
        data = storage.load_data()
        self.assertEqual(len(data), 0)

    def test_invalid_cost(self):
        with self.assertRaises(ValueError):
            utils.validate_cost(0.0)
        with self.assertRaises(ValueError):
            utils.validate_cost(-5.0)

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            utils.validate_date("2026-13-40")

    def test_analytics_calculations(self):
        manager.add_subscription("Netflix", 10.0, "monthly", "2026-10-01")
        manager.add_subscription("Prime", 120.0, "yearly", "2026-10-01")
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        analytics.show_analytics()
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        # Monthly total: 10 + (120/12) = 20.00
        # Yearly total: (10*12) + 120 = 240.00
        self.assertIn("Total Monthly Cost:    $20.00", output)
        self.assertIn("Total Yearly Cost:     $240.00", output)
        
    def test_storage_load_save(self):
        manager.add_subscription("Test", 10.0, "monthly", "2026-10-01")
        data = storage.load_data()
        self.assertEqual(len(data), 1)
        
        # Test corrupt data handling
        with open(self.temp_file, 'w') as f:
            f.write("{invalid json")
            
        data = storage.load_data()
        self.assertEqual(len(data), 0)


class TestCategoryFeature(unittest.TestCase):
    """Tests for subscription category support."""

    def setUp(self):
        self.fd, self.temp_file = tempfile.mkstemp(suffix='.json')
        storage.set_data_file(self.temp_file)
        with open(self.temp_file, 'w') as f:
            f.write("[]")

    def tearDown(self):
        os.close(self.fd)
        os.remove(self.temp_file)

    # ------------------------------------------------------------------
    # Category creation
    # ------------------------------------------------------------------

    def test_add_subscription_with_category(self):
        """A subscription added with an explicit category stores it correctly."""
        manager.add_subscription("Spotify", 9.99, "monthly", "2026-10-01",
                                 category="Entertainment")
        data = storage.load_data()
        self.assertEqual(data[0].category, "Entertainment")

    def test_add_subscription_default_category(self):
        """A subscription added without a category defaults to 'Other'."""
        manager.add_subscription("MiscTool", 5.0, "monthly", "2026-10-01")
        data = storage.load_data()
        self.assertEqual(data[0].category, "Other")

    # ------------------------------------------------------------------
    # Category update
    # ------------------------------------------------------------------

    def test_update_category(self):
        """update_subscription can change an existing category."""
        manager.add_subscription("Notion", 8.0, "monthly", "2026-10-01",
                                 category="Other")
        sub_id = storage.load_data()[0].sub_id

        manager.update_subscription(sub_id, category="Productivity")
        data = storage.load_data()
        self.assertEqual(data[0].category, "Productivity")

    def test_update_category_does_not_change_other_fields(self):
        """Updating only the category leaves cost, cycle, and name intact."""
        manager.add_subscription("GitHub", 4.0, "monthly", "2026-10-01",
                                 category="Other")
        sub_id = storage.load_data()[0].sub_id

        manager.update_subscription(sub_id, category="Software")
        sub = storage.load_data()[0]
        self.assertEqual(sub.name, "GitHub")
        self.assertEqual(sub.cost, 4.0)
        self.assertEqual(sub.cycle, "monthly")
        self.assertEqual(sub.category, "Software")

    # ------------------------------------------------------------------
    # Backward compatibility
    # ------------------------------------------------------------------

    def test_old_record_without_category_defaults_to_other(self):
        """
        Records serialised before the category field was added (i.e. no
        'category' key in JSON) must still load and default to 'Other'.
        """
        import json
        old_record = [
            {"id": 1, "name": "LegacySub", "cost": 7.0,
             "cycle": "monthly", "next_date": "2026-10-01"}
        ]
        with open(self.temp_file, 'w') as f:
            json.dump(old_record, f)

        data = storage.load_data()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].category, "Other")

    # ------------------------------------------------------------------
    # Category validation
    # ------------------------------------------------------------------

    def test_validate_category_accepts_valid_values(self):
        """validate_category returns the canonical name for valid inputs."""
        self.assertEqual(utils.validate_category("Entertainment"), "Entertainment")
        self.assertEqual(utils.validate_category("education"), "Education")
        self.assertEqual(utils.validate_category("CLOUD STORAGE"), "Cloud Storage")

    def test_validate_category_rejects_unknown_values(self):
        """validate_category raises ValueError for unrecognised categories."""
        with self.assertRaises(ValueError):
            utils.validate_category("Gaming")

    # ------------------------------------------------------------------
    # Category analytics
    # ------------------------------------------------------------------

    def test_analytics_by_category(self):
        """Analytics output includes per-category spending lines."""
        manager.add_subscription("Netflix", 10.0, "monthly", "2026-10-01",
                                 category="Entertainment")
        manager.add_subscription("Spotify", 5.0, "monthly", "2026-10-01",
                                 category="Entertainment")
        manager.add_subscription("Notion", 8.0, "monthly", "2026-10-01",
                                 category="Productivity")

        captured = io.StringIO()
        sys.stdout = captured
        analytics.show_analytics()
        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        # Entertainment: 10 + 5 = 15.00 /month
        self.assertIn("Entertainment", output)
        self.assertIn("$15.00", output)
        # Productivity: 8.00 /month
        self.assertIn("Productivity", output)
        self.assertIn("$8.00", output)

    def test_analytics_most_expensive(self):
        """Analytics identifies the single most expensive subscription."""
        manager.add_subscription("Cheap", 5.0, "monthly", "2026-10-01",
                                 category="Other")
        manager.add_subscription("Expensive", 50.0, "monthly", "2026-10-01",
                                 category="Software")

        captured = io.StringIO()
        sys.stdout = captured
        analytics.show_analytics()
        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        self.assertIn("Most Expensive", output)
        self.assertIn("Expensive", output)

    def test_analytics_total_count(self):
        """Analytics reports the correct total number of subscriptions."""
        manager.add_subscription("A", 1.0, "monthly", "2026-10-01")
        manager.add_subscription("B", 2.0, "monthly", "2026-10-01")
        manager.add_subscription("C", 3.0, "monthly", "2026-10-01")

        captured = io.StringIO()
        sys.stdout = captured
        analytics.show_analytics()
        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        self.assertIn("Total Subscriptions:   3", output)

    def test_yearly_subscription_monthly_equivalent_in_analytics(self):
        """A yearly subscription is counted as cost/12 per month in analytics."""
        manager.add_subscription("AnnualPlan", 120.0, "yearly", "2026-10-01",
                                 category="Cloud Storage")

        captured = io.StringIO()
        sys.stdout = captured
        analytics.show_analytics()
        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        # $120/year = $10/month
        self.assertIn("Total Monthly Cost:    $10.00", output)
        self.assertIn("Total Yearly Cost:     $120.00", output)


class TestSavingsAnalyzer(unittest.TestCase):
    """
    Unit tests for the Savings Analyzer.

    All tests call calculate_savings() directly with in-memory Subscription
    objects, so no temporary file or storage.set_data_file() is required.
    """

    def _make_sub(self, sub_id, name, cost, cycle, category="Other"):
        """Helper: construct a Subscription without touching disk."""
        from src.models import Subscription
        return Subscription(sub_id, name, cost, cycle, "2026-10-01", category)

    # ------------------------------------------------------------------
    # Single subscription selections
    # ------------------------------------------------------------------

    def test_single_monthly_subscription(self):
        """Selecting one monthly sub saves exactly its cost per month."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Netflix", 15.0, "monthly")]
        result = calculate_savings(subs, "1")
        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["monthly"], 15.0)
        self.assertAlmostEqual(result["yearly"], 180.0)

    def test_single_yearly_subscription(self):
        """Selecting one yearly sub converts to cost/12 per month."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Adobe CC", 120.0, "yearly")]
        result = calculate_savings(subs, "1")
        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["monthly"], 10.0)
        self.assertAlmostEqual(result["yearly"], 120.0)

    # ------------------------------------------------------------------
    # Multiple subscriptions
    # ------------------------------------------------------------------

    def test_multiple_subscriptions(self):
        """Savings are summed correctly across multiple selected IDs."""
        from src.savings import calculate_savings
        subs = [
            self._make_sub(1, "Netflix",  10.0, "monthly"),
            self._make_sub(2, "Spotify",   5.0, "monthly"),
            self._make_sub(3, "Notion",    8.0, "monthly"),
        ]
        result = calculate_savings(subs, "1, 2, 3")
        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["monthly"], 23.0)
        self.assertAlmostEqual(result["yearly"],  276.0)

    def test_mixed_monthly_and_yearly(self):
        """Monthly and yearly subs are combined using monthly-equivalent logic."""
        from src.savings import calculate_savings
        subs = [
            self._make_sub(1, "Spotify",   9.99, "monthly"),   # 9.99/mo
            self._make_sub(2, "GitHub",   48.0,  "yearly"),    # 4.00/mo
        ]
        result = calculate_savings(subs, "1, 2")
        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["monthly"], 9.99 + 4.0, places=2)
        self.assertAlmostEqual(result["yearly"],  (9.99 + 4.0) * 12, places=2)

    # ------------------------------------------------------------------
    # Yearly savings equals monthly * 12
    # ------------------------------------------------------------------

    def test_yearly_savings_equals_monthly_times_12(self):
        """yearly savings must always equal monthly savings * 12."""
        from src.savings import calculate_savings
        subs = [
            self._make_sub(1, "A", 7.50,  "monthly"),
            self._make_sub(2, "B", 99.0,  "yearly"),
        ]
        result = calculate_savings(subs, "1, 2")
        self.assertAlmostEqual(result["yearly"], result["monthly"] * 12, places=6)

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def test_nonexistent_id_returns_error(self):
        """An ID that does not exist produces an error, not a crash."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Netflix", 10.0, "monthly")]
        result = calculate_savings(subs, "99")
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIn("99", result["errors"][0])

    def test_non_integer_id_returns_error(self):
        """Non-integer tokens produce a clear error message."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Netflix", 10.0, "monthly")]
        result = calculate_savings(subs, "abc")
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIn("abc", result["errors"][0])

    def test_empty_input_returns_error(self):
        """Empty input produces a clear error message."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Netflix", 10.0, "monthly")]
        result = calculate_savings(subs, "")
        self.assertTrue(len(result["errors"]) > 0)

    def test_whitespace_only_input_returns_error(self):
        """Whitespace-only input is treated the same as empty input."""
        from src.savings import calculate_savings
        subs = [self._make_sub(1, "Netflix", 10.0, "monthly")]
        result = calculate_savings(subs, "   ")
        self.assertTrue(len(result["errors"]) > 0)

    def test_no_subscriptions_deleted(self):
        """calculate_savings must never mutate the subscription list."""
        from src.savings import calculate_savings
        subs = [
            self._make_sub(1, "Netflix", 10.0, "monthly"),
            self._make_sub(2, "Spotify",  5.0, "monthly"),
        ]
        calculate_savings(subs, "1")
        self.assertEqual(len(subs), 2)   # list is unchanged


class TestRenewalDateHandling(unittest.TestCase):
    """
    Tests for automatic renewal-date advancement.

    All date-arithmetic tests call advance_renewal_date() or
    refresh_renewal_dates() directly with an explicit reference_date so
    results are deterministic and independent of the system clock.
    """

    # Fixed reference date used throughout this class (today's date for tests)
    REF = date(2026, 9, 26)

    # ------------------------------------------------------------------
    # Single-cycle advancement
    # ------------------------------------------------------------------

    def test_past_monthly_advances_correctly(self):
        """A past monthly date is advanced by one month at a time until future."""
        # 2026-08-01 + 1m → 2026-09-01  (< REF 2026-09-26)
        # 2026-09-01 + 1m → 2026-10-01  (>= REF) ✓
        result = utils.advance_renewal_date("2026-08-01", "monthly", self.REF)
        self.assertEqual(result, "2026-10-01")

    def test_past_yearly_advances_correctly(self):
        """A past yearly date is advanced by one year at a time until future."""
        # 2025-06-01 + 1y → 2026-06-01  (< REF 2026-09-26)
        # 2026-06-01 + 1y → 2027-06-01  (>= REF) ✓
        result = utils.advance_renewal_date("2025-06-01", "yearly", self.REF)
        self.assertEqual(result, "2027-06-01")

    # ------------------------------------------------------------------
    # Multiple missed cycles
    # ------------------------------------------------------------------

    def test_multiple_missed_monthly_cycles(self):
        """A date several months in the past advances through all missed cycles."""
        # 2026-06-01 → Jul → Aug → Sep 01 (< REF) → Oct 01 ✓
        result = utils.advance_renewal_date("2026-06-01", "monthly", self.REF)
        self.assertEqual(result, "2026-10-01")

    # ------------------------------------------------------------------
    # Month-end clamping
    # ------------------------------------------------------------------

    def test_monthly_jan31_clamps_at_month_end(self):
        """
        Jan 31 + 1 month must become Feb 28 (non-leap), not crash.
        The date then continues advancing until it passes the reference.
        """
        ref = date(2027, 3, 1)
        # 2027-01-31 + 1m → 2027-02-28 (clamped, non-leap; < ref 2027-03-01)
        # 2027-02-28 + 1m → 2027-03-28 (day preserved as 28; >= ref) ✓
        result = utils.advance_renewal_date("2027-01-31", "monthly", ref)
        self.assertEqual(result, "2027-03-28")

    # ------------------------------------------------------------------
    # Leap-year edge case
    # ------------------------------------------------------------------

    def test_yearly_leap_day_clamps_in_non_leap_year(self):
        """
        Feb 29 (leap year) + 1 year must become Feb 28 in non-leap years.
        Advancement continues until the date is on or after the reference.
        """
        ref = date(2026, 1, 1)
        # 2024-02-29 + 1y → 2025-02-28 (clamped, 2025 not leap; < ref 2026-01-01)
        # 2025-02-28 + 1y → 2026-02-28 (2026 not leap; >= ref) ✓
        result = utils.advance_renewal_date("2024-02-29", "yearly", ref)
        self.assertEqual(result, "2026-02-28")

    # ------------------------------------------------------------------
    # Dates that must NOT change
    # ------------------------------------------------------------------

    def test_today_does_not_advance(self):
        """A date equal to reference_date is returned unchanged."""
        result = utils.advance_renewal_date("2026-09-26", "monthly", self.REF)
        self.assertEqual(result, "2026-09-26")

    def test_future_date_does_not_change(self):
        """A date already in the future is returned unchanged."""
        result = utils.advance_renewal_date("2027-01-01", "monthly", self.REF)
        self.assertEqual(result, "2027-01-01")

    # ------------------------------------------------------------------
    # refresh_renewal_dates bulk helper
    # ------------------------------------------------------------------

    def test_refresh_returns_true_when_any_date_changed(self):
        """refresh_renewal_dates() returns True when at least one date is stale."""
        from src.models import Subscription
        subs = [
            Subscription(1, "Old",    10.0, "monthly", "2020-01-01"),
            Subscription(2, "Future",  5.0, "monthly", "2027-01-01"),
        ]
        changed = utils.refresh_renewal_dates(subs, self.REF)
        self.assertTrue(changed)
        # Only the stale sub was advanced; the future one is unchanged
        self.assertNotEqual(subs[0].next_date, "2020-01-01")
        self.assertEqual(subs[1].next_date, "2027-01-01")

    def test_refresh_returns_false_when_all_dates_current(self):
        """refresh_renewal_dates() returns False when no dates need advancing."""
        from src.models import Subscription
        subs = [
            Subscription(1, "A", 10.0, "monthly", "2027-01-01"),
            Subscription(2, "B",  5.0, "yearly",  "2027-06-01"),
        ]
        changed = utils.refresh_renewal_dates(subs, self.REF)
        self.assertFalse(changed)

    # ------------------------------------------------------------------
    # Persistence: updated dates must be written back to disk
    # ------------------------------------------------------------------

    def test_updated_date_is_persisted_to_disk(self):
        """
        When load_data() advances a stale date it must write the corrected
        record back to the JSON file so the change survives the next load.
        """
        fd, temp_file = tempfile.mkstemp(suffix='.json')
        original_data_file = storage.DATA_FILE
        try:
            storage.set_data_file(temp_file)

            # Write a record with an obviously stale date
            stale = [
                {"id": 1, "name": "OldSub", "cost": 9.99,
                 "cycle": "monthly", "next_date": "2020-06-15",
                 "category": "Other"}
            ]
            with open(temp_file, 'w') as f:
                json.dump(stale, f)

            # load_data() should advance the date and persist it
            in_memory = storage.load_data()

            # Verify the in-memory object was advanced
            self.assertNotEqual(in_memory[0].next_date, "2020-06-15")

            # Verify the disk was also updated to match
            with open(temp_file, 'r') as f:
                on_disk = json.load(f)
            self.assertEqual(on_disk[0]["next_date"], in_memory[0].next_date)

        finally:
            storage.set_data_file(original_data_file)
            os.close(fd)
            os.remove(temp_file)


class TestSearchFilter(unittest.TestCase):
    """
    Tests for the search/filter feature.

    All tests call filter_subscriptions() directly with in-memory
    Subscription objects — no disk I/O required.
    """

    def _make_sub(self, sub_id, name, cost, cycle, category="Other"):
        from src.models import Subscription
        return Subscription(sub_id, name, cost, cycle, "2026-10-01", category)

    def _sample_subs(self):
        return [
            self._make_sub(1, "Netflix",      15.99, "monthly", "Entertainment"),
            self._make_sub(2, "Spotify",       9.99, "monthly", "Entertainment"),
            self._make_sub(3, "Google Drive",  1.99, "monthly", "Cloud Storage"),
            self._make_sub(4, "GitHub Pro",   48.00, "yearly",  "Software"),
            self._make_sub(5, "Notion",        8.00, "monthly", "Productivity"),
        ]

    # ------------------------------------------------------------------
    # Name search
    # ------------------------------------------------------------------

    def test_search_exact_name(self):
        """Exact name matches the subscription."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(), term="Netflix")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Netflix")

    def test_search_case_insensitive(self):
        """Name search is case-insensitive."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(), term="netflix")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Netflix")

    def test_search_partial_name(self):
        """Partial string matches subscription names."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(), term="oo")
        names = [r.name for r in results]
        # "Google Drive" contains "oo"
        self.assertIn("Google Drive", names)

    # ------------------------------------------------------------------
    # Category filter
    # ------------------------------------------------------------------

    def test_filter_category_only(self):
        """Filtering by category alone returns all subs in that category."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(), category="Entertainment")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r.category, "Entertainment")

    # ------------------------------------------------------------------
    # Combined
    # ------------------------------------------------------------------

    def test_combined_name_and_category(self):
        """Name + category filters are applied together (AND logic)."""
        from src.search import filter_subscriptions
        subs = self._sample_subs()
        # "Spotify" is Entertainment; searching "spo" + Entertainment → 1 match
        results = filter_subscriptions(subs, term="spo", category="Entertainment")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Spotify")

    def test_combined_name_and_wrong_category(self):
        """Name matches but category does not → zero results."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(),
                                       term="Netflix", category="Software")
        self.assertEqual(len(results), 0)

    # ------------------------------------------------------------------
    # No results
    # ------------------------------------------------------------------

    def test_no_matching_results(self):
        """A search term that matches nothing returns an empty list."""
        from src.search import filter_subscriptions
        results = filter_subscriptions(self._sample_subs(), term="xyzzy")
        self.assertEqual(len(results), 0)


class TestExportReport(unittest.TestCase):
    """
    Tests for the CSV export feature.

    All tests write to a temporary directory so the real ``reports/`` folder
    is never touched.
    """

    def setUp(self):
        self.fd, self.temp_data = tempfile.mkstemp(suffix='.json')
        storage.set_data_file(self.temp_data)
        with open(self.temp_data, 'w') as f:
            f.write("[]")

        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, "test_report.csv")

    def tearDown(self):
        os.close(self.fd)
        os.remove(self.temp_data)
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    def _add_subs(self):
        manager.add_subscription("Netflix", 15.99, "monthly", "2027-10-01",
                                 category="Entertainment")
        manager.add_subscription("GitHub",  48.00, "yearly",  "2027-11-01",
                                 category="Software")

    # ------------------------------------------------------------------
    # File creation
    # ------------------------------------------------------------------

    def test_csv_file_is_created(self):
        """The export command creates a CSV file at the given path."""
        from src.export import generate_report
        self._add_subs()
        subs = storage.load_data()
        generate_report(subs, self.csv_path)
        self.assertTrue(os.path.exists(self.csv_path))

    # ------------------------------------------------------------------
    # Headers
    # ------------------------------------------------------------------

    def test_csv_contains_expected_headers(self):
        """The first row of the CSV contains the canonical header names."""
        import csv as csv_mod
        from src.export import generate_report, CSV_HEADERS
        self._add_subs()
        subs = storage.load_data()
        generate_report(subs, self.csv_path)

        with open(self.csv_path, 'r') as f:
            reader = csv_mod.reader(f)
            headers = next(reader)
        self.assertEqual(headers, CSV_HEADERS)

    # ------------------------------------------------------------------
    # Data rows
    # ------------------------------------------------------------------

    def test_csv_contains_subscription_data(self):
        """Data rows contain the correct subscription name and cost."""
        import csv as csv_mod
        from src.export import generate_report
        self._add_subs()
        subs = storage.load_data()
        generate_report(subs, self.csv_path)

        with open(self.csv_path, 'r') as f:
            reader = csv_mod.reader(f)
            next(reader)  # skip header
            rows = list(reader)

        self.assertEqual(len(rows), 2)
        # First row is Netflix
        self.assertEqual(rows[0][1], "Netflix")
        self.assertEqual(rows[0][2], "15.99")

    # ------------------------------------------------------------------
    # Monthly / yearly equivalents
    # ------------------------------------------------------------------

    def test_yearly_sub_monthly_equivalent(self):
        """A yearly subscription's monthly equivalent is cost / 12."""
        import csv as csv_mod
        from src.export import generate_report
        self._add_subs()
        subs = storage.load_data()
        generate_report(subs, self.csv_path)

        with open(self.csv_path, 'r') as f:
            reader = csv_mod.reader(f)
            next(reader)
            rows = list(reader)

        # GitHub is the second row (yearly, $48)
        github_row = rows[1]
        self.assertEqual(github_row[6], "4.00")   # monthly equivalent
        self.assertEqual(github_row[7], "48.00")   # yearly equivalent

    def test_monthly_sub_yearly_equivalent(self):
        """A monthly subscription's yearly equivalent is cost * 12."""
        import csv as csv_mod
        from src.export import generate_report
        self._add_subs()
        subs = storage.load_data()
        generate_report(subs, self.csv_path)

        with open(self.csv_path, 'r') as f:
            reader = csv_mod.reader(f)
            next(reader)
            rows = list(reader)

        # Netflix is the first row (monthly, $15.99)
        netflix_row = rows[0]
        self.assertEqual(netflix_row[6], "15.99")   # monthly equivalent
        self.assertEqual(netflix_row[7], "191.88")  # yearly: 15.99 * 12

    # ------------------------------------------------------------------
    # Non-destructive
    # ------------------------------------------------------------------

    def test_export_does_not_modify_data(self):
        """Generating a report does not change the subscription data on disk."""
        from src.export import generate_report
        self._add_subs()

        before = storage.load_data()
        before_dicts = [s.to_dict() for s in before]

        generate_report(before, self.csv_path)

        after = storage.load_data()
        after_dicts = [s.to_dict() for s in after]

        self.assertEqual(before_dicts, after_dicts)


if __name__ == '__main__':
    unittest.main()
