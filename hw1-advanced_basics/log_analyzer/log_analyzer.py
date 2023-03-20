import argparse
import configparser
import logging
import re
import sys
from collections import namedtuple
from os.path import exists
from typing import Optional


#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


LOG_DATE_REGEXP = re.compile(
    r"(?P<full_date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NGINX Log analyzer script")

    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="Path to a config file",
    )

    args = parser.parse_args()
    return args


def get_config_values(
    init_config: dict, config_path: Optional[str] = None
) -> Optional[namedtuple]:
    ReportConfig = namedtuple("ReportConfig", ["report_size", "report_dir", "log_dir"])

    config = configparser.ConfigParser()
    config.read_dict({"DEFAULT": init_config})

    if config_path:
        config.read(config_path, encoding="utf-8")

    try:
        report_size = config.get("LOG_ANALYZER", "REPORT_SIZE")
        report_dir = config.get("LOG_ANALYZER", "REPORT_DIR")
        log_dir = config.get("LOG_ANALYZER", "LOG_DIR")
    except configparser.NoOptionError:
        return None

    return ReportConfig(report_size, report_dir, log_dir)


def init_logging_config(filename: Optional[str] = None, level: str = "INFO") -> None:
    logging.basicConfig(
        filename=filename,
        filemode="a",
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        level=getattr(logging, level),
    )


def main() -> None:
    args = parse_arguments()
    if not exists(args.config_path):
        sys.exit("No such config file!")

    report_config = get_config_values(config, args.config_path)
    if not report_config:
        sys.exit("There is no valid config!")

    init_logging_config()


if __name__ == "__main__":
    main()
