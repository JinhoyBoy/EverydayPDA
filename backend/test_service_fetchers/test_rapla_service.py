import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.rapla_service import get_rapla_schedule

class TestGetRaplaSchedule(unittest.TestCase):

    @patch('backend.service_fetchers.rapla_service.requests.get')
    @patch('backend.service_fetchers.rapla_service.is_valid_date')
    def test_get_rapla_schedule_success(self, mock_is_valid_date, mock_get):
        mock_is_valid_date.return_value = "2024-04-11"

        mock_ics = (
            "BEGIN:VEVENT\n"
            "DTSTAMP:20240411T080000Z\n"
            "SUMMARY:Mathe-Vorlesung\n"
            "DTSTART;TZID=Europe/Berlin:20240411T090000\n"
            "DTEND;TZID=Europe/Berlin:20240411T103000\n"
            "LOCATION:Hörsaal 1\n"
            "END:VEVENT\n"
        )

        mock_response = MagicMock()
        mock_response.text = mock_ics
        mock_get.return_value = mock_response

        result = get_rapla_schedule(["2024-04-11"])

        expected = {
            "Mathe-Vorlesung": {
                "start": "09:00",
                "end": "10:30",
                "location": "Hörsaal 1"
            }
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.rapla_service.requests.get')
    @patch('backend.service_fetchers.rapla_service.is_valid_date')
    def test_get_rapla_schedule_no_match(self, mock_is_valid_date, mock_get):
        mock_is_valid_date.return_value = "2024-04-11"

        mock_ics = (
            "BEGIN:VEVENT\n"
            "DTSTAMP:20240410T080000Z\n"
            "SUMMARY:Physik\n"
            "DTSTART;TZID=Europe/Berlin:20240410T100000\n"
            "DTEND;TZID=Europe/Berlin:20240410T113000\n"
            "LOCATION:Hörsaal 2\n"
            "END:VEVENT\n"
        )

        mock_response = MagicMock()
        mock_response.text = mock_ics
        mock_get.return_value = mock_response

        result = get_rapla_schedule(["2024-04-11"])
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
