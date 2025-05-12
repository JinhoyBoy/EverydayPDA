import unittest
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.helpers import is_valid_date

class TestHelpers(unittest.TestCase):

    def test_valid_date_yyyy_mm_dd(self):
        self.assertEqual(is_valid_date("2025-04-15"), "2025-04-15")

    def test_valid_date_dd_mm_yyyy(self):
        self.assertEqual(is_valid_date("15.04.2025"), "2025-04-15")

    def test_missing_year(self):
        current_year = datetime.now().year
        self.assertEqual(is_valid_date("15.04."), f"{current_year}-04-15")

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            is_valid_date("15/04/2025")

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            is_valid_date("32.04.2025")

if __name__ == "__main__":
    unittest.main()