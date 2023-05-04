import socket
import logging
import traceback
from typing import Optional


def init_logging_config(filename: Optional[str] = None, level: str = "INFO") -> None:
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


def check_valid_ip(ip_addres: str) -> bool:
    try:
        socket.inet_aton(ip_addres)
        return "True"
    except socket.error:
        return "False"


def application(env, start_response):
    init_logging_config("ip2w.log")
    ip_address = env["REQUEST_URI"].replace("/ip2w/", "")
    logging.debug(env)
    response = check_valid_ip(ip_address)
    start_response("200 OK", [("Content-Type", "text/html")])
    return [bytes(response, encoding="utf-8")]
