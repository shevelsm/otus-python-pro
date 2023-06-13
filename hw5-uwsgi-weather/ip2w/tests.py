import unittest

from ip2w import (
    CONFIG_PATH,
    HTTP_200_OK,
    check_valid_ip,
    get_city_by_ip,
    get_config_values,
    load_weather_data,
)

config = get_config_values(CONFIG_PATH)
BAD_GATEWAY = 502


def cases(cases_):
    """Decorator to make tests in time of initialization"""

    def wrapper(func):
        def inner(*args):
            for case in cases_:
                new_args = args + (case if (isinstance(case, tuple)) else (case,))
                func(*new_args)

        return inner

    return wrapper


class TestAPI(unittest.TestCase):
    @cases(
        [
            ("198.100.200.10", "Eden Prairie,US"),
            ("176.14.221.123", "Mytishchi,RU"),
            ("127.0.0.1", "No country and city for the 127.0.0.1"),
        ]
    )
    def test_correct_city(self, ip_address, city_correct):
        _, city = get_city_by_ip(ip=ip_address, config=config)
        self.assertEqual(city, city_correct)

    @cases(
        [
            ("10.10.11.12", True),
            ("0.255.255.0", True),
            ("256.2.100.0", False),
            ("1.1.1.a2", False),
            ("100.1.1.1.1", False),
        ]
    )
    def test_valid_ip(self, ip_address, bool_value):
        """Is ip checked correctly?"""
        self.assertEqual(check_valid_ip(ip_address), bool_value)

    @cases(
        [
            "198.100.200.10",
            "176.14.221.123",
        ]
    )
    def test_functional_good_ip(self, ip):
        code, response = load_weather_data(ip, config)
        self.assertEqual(code, HTTP_200_OK)
        self.assertEqual(len(response), 3)
        self.assertTrue(response.get("temp"))
        self.assertTrue(response.get("city"))


if __name__ == "__main__":
    unittest.main()
