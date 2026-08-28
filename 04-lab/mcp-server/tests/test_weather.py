import unittest
import logging
from unittest.mock import AsyncMock, patch

import weather


class WeatherToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_current_weather_uses_mock_data_without_api(self):
        with patch("weather.make_weather_request", new=AsyncMock(return_value=None)):
            result = await weather.get_current_weather("  Hanoi  ")

        self.assertIn("Current Weather for Hanoi", result)
        self.assertIn("Temperature: 29.0°C", result)

    async def test_forecast_respects_requested_day_count(self):
        with patch("weather.make_weather_request", new=AsyncMock(return_value=None)):
            result = await weather.get_forecast("Brisbane", days=1)

        self.assertIn("2026-08-28", result)
        self.assertNotIn("2026-08-29", result)
        self.assertNotIn("2026-08-30", result)

    async def test_forecast_clamps_to_free_tier_range(self):
        request = AsyncMock(return_value=None)
        with patch("weather.make_weather_request", new=request):
            one_day = await weather.get_forecast("Hanoi", days=0)
            three_days = await weather.get_forecast("Hanoi", days=99)

        self.assertEqual(one_day.count("\n---\n"), 1)
        self.assertEqual(three_days.count("\n---\n"), 3)
        self.assertEqual(request.await_args_list[0].args[1]["days"], "1")
        self.assertEqual(request.await_args_list[1].args[1]["days"], "3")

    async def test_empty_city_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "city must not be empty"):
            await weather.get_current_weather("   ")

        with self.assertRaisesRegex(ValueError, "city must not be empty"):
            await weather.get_forecast("")

    async def test_health_check(self):
        result = await weather.health_check()
        self.assertIn("running", result)

    def test_mock_city_lookup_is_trimmed_and_case_insensitive(self):
        result = weather.get_mock_data("  BRISBANE ")
        self.assertEqual(result["location"]["name"], "Brisbane")

    def test_empty_location_fields_are_omitted(self):
        location = {"name": "Hanoi", "region": "", "country": "Vietnam"}
        self.assertEqual(weather.format_location(location), "Hanoi, Vietnam")

    def test_httpx_info_logs_are_disabled_to_protect_api_key(self):
        self.assertGreaterEqual(logging.getLogger("httpx").level, logging.WARNING)


if __name__ == "__main__":
    unittest.main()
