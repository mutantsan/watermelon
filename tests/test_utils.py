import pytest

import app.utils as utils
import app.const as const


class TestGetTimezoneByCity:
    def test_non_existing_city(self):
        assert utils.get_timezone_by_city("#") == const.DEFAULT_TZ

    @pytest.mark.parametrize(
        "city, timezone",
        [
            ("Warsaw", "Europe/Warsaw"),
            ("Киев", "Europe/Kyiv"),
            ("Київ", "Europe/Kyiv"),
            ("Нью-Йорк", "America/New_York"),
            ("Токіо", "Asia/Tokyo"),
            ("Tokyo", "Asia/Tokyo"),
            ("Сараєво", "Europe/Sarajevo"),
        ],
    )
    def test_existing_cities(self, city: str, timezone: str):
        assert utils.get_timezone_by_city(city) == timezone
