import argparse
import configparser
import gzip
import logging
import os
import re
import sys
import traceback
from datetime import datetime
from collections import namedtuple
from typing import Callable, Iterator, Optional


#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


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
        report_size = config.get("DEFAULT", "REPORT_SIZE")
        report_dir = config.get("DEFAULT", "REPORT_DIR")
        log_dir = config.get("DEFAULT", "LOG_DIR")
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None

    return ReportConfig(report_size, report_dir, log_dir)


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


def get_the_last_log_file(config: type) -> str:
    dt_format = "%Y%m%d"
    dt_regex = re.compile(
        r"^nginx-access-ui\.log-(?P<full_date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))"
    )
    log_dir = config.log_dir
    if not log_dir or not os.path.exists(log_dir) or not os.path.isdir(log_dir):
        logging.error("Log directory was not found. LOG_DIR: {}".format(log_dir))
        return None

    last_filename = None
    last_date = datetime.strptime("19700101", dt_format)
    LastLog = namedtuple("LastLog", ["filename", "date"])

    for filename in os.listdir(log_dir):
        path = os.path.join(log_dir, filename)
        m = dt_regex.match(filename)

        try:
            dt = datetime.strptime(m.group("full_date"), dt_format)
        except ValueError:
            logging.error(
                "Bad log_date ({}) for log_file {}".format(
                    filename, m.group("full_date")
                )
            )
            continue

        if dt and dt > last_date:
            last_filename = path
            last_date = dt

    return LastLog(last_filename, last_date)


def get_report_name(report_dt: datetime.date) -> Optional[str]:
    return "report-{0}.{1}.{2}.html".format(
        report_dt.year, report_dt.month, report_dt.day
    )


def check_report_exists(log_path: str, report_file: str) -> bool:
    if report_file:
        report_path = os.path.join(log_path, report_file)
        if os.path.exists(report_path) and os.path.isfile(report_path):
            return True
    return False


def get_open_log_func(filename: str) -> Callable:
    if re.search(r"[.]gz$", filename):
        return gzip.open
    else:
        return open


def read_log_file(log_file: str, encoding: str = "utf-8") -> Iterator[str]:
    open_f = get_open_log_func(log_file)
    with open_f(log_file, encoding=encoding) as file:
        for line in file:
            yield line


def main() -> None:
    args = parse_arguments()
    if args.config_path and not os.path.exists(args.config_path):
        sys.exit("No such config file!")

    report_config = get_config_values(config, args.config_path)
    if not report_config:
        sys.exit("There is no valid config!")

    if not init_logging_config(level="DEBUG"):
        sys.exit("Check init_logging_config() usage!")

    LastLog = get_the_last_log_file(report_config)
    if not LastLog:
        sys.exit("Can't get last log file! Finishing script...")
    logging.debug("The last log file is - {}".format(LastLog.filename))

    report_name = get_report_name(LastLog.date)
    logging.debug("Result file name will be - {}".format(report_name))

    if check_report_exists(report_config.report_dir, report_name):
        sys.exit("The report file ({}) already exists".format(report_name))

    logging.info("Log analyzer script has finished the work!")


if __name__ == "__main__":
    main()
