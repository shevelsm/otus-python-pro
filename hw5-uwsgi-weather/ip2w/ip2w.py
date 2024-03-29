import json
import logging
import socket
import traceback
from configparser import ConfigParser

import requests

CONFIG_PATH = "config.ini"
IPINFO_URL = "https://ipinfo.io/{}"
OPENWEATHER_URL = (
    "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&APPID={}"
)

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_500_INTERNAL_ERROR = 500


def init_logging_config(filename=None, level="INFO"):
    try:
        logging.basicConfig(
            filename=filename,
            filemode="a",
            format="[%(asctime)s] %(levelname).1s %(message)s",
            datefmt="%Y.%m.%d %H:%M:%S",
            level=getattr(logging, level),
        )
    except TypeError:
        logging.error("Error initializing the logging system")
        traceback.print_stack()
        return False

    return True


def get_config_values(config_path=None):
    config = ConfigParser()
    config.read(config_path, encoding="utf-8")

    return config


def check_valid_ip(ip) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def perform_request(url, config):
    retries = int(config["ip2w"]["retries"])
    timeout = int(config["ip2w"]["timeout"])
    for _ in range(retries):
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return HTTP_200_OK, response.json()
    return HTTP_500_INTERNAL_ERROR, "Maximum retries exceeded"


def get_city_by_ip(ip, config):
    code, response = perform_request(IPINFO_URL.format(ip), config)
    if code != HTTP_200_OK:
        return code, response

    city = response.get("city")
    country = response.get("country")
    if not (city and country):
        return HTTP_500_INTERNAL_ERROR, "No country and city for the {}".format(ip)

    return HTTP_200_OK, "{},{}".format(city, country)


def get_weather_by_city(city, config):
    code, response = perform_request(
        OPENWEATHER_URL.format(city, config["ip2w"]["weather_api_key"]), config
    )
    if code != HTTP_200_OK:
        return code, response

    logging.debug("OPENWEATHER response: {}".format(response))

    if response.get("cod") != HTTP_200_OK:
        return HTTP_500_INTERNAL_ERROR, response.get("message")

    temp = str(response["main"]["temp"])
    conditions = ", ".join(
        [condition["description"] for condition in response["weather"]]
    )
    weather = {
        "city": response["name"],
        "temp": temp if temp.startswith("-") else "+" + temp,
        "conditions": conditions,
    }
    return HTTP_200_OK, weather


def load_weather_data(ip, config):
    code, city = get_city_by_ip(ip, config)
    if code != HTTP_200_OK:
        return code, city

    code, weather = get_weather_by_city(city, config)
    logging.debug("load_weather response: {}".format(weather))

    return code, weather


def application(env, start_response):
    config = get_config_values(CONFIG_PATH)
    init_logging_config(config["ip2w"]["log_path"], config["ip2w"]["log_level"])
    ip_address = env["REQUEST_URI"].replace("/ip2w/", "")
    logging.info("IP address from the request - {}".format(ip_address))
    if not check_valid_ip(ip_address):
        code, response = (
            HTTP_400_BAD_REQUEST,
            "Incorrect IP address - {}. Please try another one...".format(ip_address),
        )
    else:
        code, response = load_weather_data(ip_address, config)

    logging.info("{}, {}".format(code, response))

    if not isinstance(response, str):
        response = json.dumps(response)

    start_response(str(code), [("Content-Type", "text/html")])
    return [bytes(response, encoding="utf-8")]
