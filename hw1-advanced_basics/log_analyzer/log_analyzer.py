import argparse
import gzip
import json
import logging
import os
import re
from statistics import median
import sys
import traceback
from configparser import ConfigParser
from datetime import datetime
from collections import namedtuple
from typing import Callable, Iterator, NamedTuple, Optional


#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "REPORT_TEMPLATE": "report.html",
    "MAX_ERROR_RATE": 0.8,
}
LastLogFile = namedtuple("LastLogFile", ["filename", "date"])
LogLine = namedtuple("LogLine", ["url", "time"])
LogData = namedtuple(
    "LogData", ["url_data", "total_time", "total_count", "errors_count"]
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


def get_config_values(init_config: dict, config_path: str) -> ConfigParser:
    config = ConfigParser()
    config.read_dict({"DEFAULT": init_config})
    config.read(config_path, encoding="utf-8")

    return config


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


def get_the_last_log_file(config: ConfigParser) -> NamedTuple:
    dt_format = "%Y%m%d"
    dt_regex = re.compile(
        r"^nginx-access-ui\.log-(?P<full_date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))"
    )
    log_dir = config.get("DEFAULT", "LOG_DIR")
    if not log_dir or not os.path.exists(log_dir) or not os.path.isdir(log_dir):
        logging.error("Log directory was not found. LOG_DIR: {}".format(log_dir))
        return None

    last_filename = None
    last_date = datetime.strptime("19700101", dt_format)

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

    return LastLogFile(last_filename, last_date)


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


def handle_log_line(line: str) -> NamedTuple:
    log_regexp = re.compile(r"\"\w+ (?P<url>(.*?)) HTTP.* (?P<time>[0-9.]+)$")
    if m := log_regexp.search(line):
        return LogLine(m.group("url"), float(m.group("time")))

    return LogLine(None, 0)


def parse_logs(filename: str) -> NamedTuple:
    url_data = {}
    total_count = 0
    total_time = 0
    errors_count = 0

    open_f = get_open_log_func(filename)
    with open_f(filename, mode="r") as log_file:
        for line in log_file:
            url, time = handle_log_line(line)

            if not (url and line):
                errors_count += 1
            total_count += 1
            total_time += time

            if url not in url_data:
                url_data[url] = [time]
            else:
                url_data[url].append(time)

    return LogData(url_data, total_time, total_count, errors_count)


def handle_log_data(log_data: NamedTuple, config: ConfigParser) -> Optional[list]:
    urls = log_data.url_data
    result = []

    error_rate = log_data.errors_count / log_data.total_count
    logging.debug("The error rate in the log is - {}".format(round(error_rate, 3)))
    max_error_rate = float(config.get("DEFAULT", "MAX_ERROR_RATE"))

    if error_rate >= max_error_rate:
        logging.error(
            "Maximum error rate {} was exceeded ({})".format(max_error_rate, error_rate)
        )
        return None

    for url in urls:
        count = len(urls[url])
        count_perc = 100 * float(count) / log_data.total_count
        time_avg = sum(urls[url]) / count
        time_max = max(urls[url])
        time_med = median(sorted(urls[url]))
        time_sum = sum(urls[url])
        time_perc = 100 * time_sum / log_data.total_time
        result.append(
            {
                "url": url,
                "count": count,
                "count_perc": round(count_perc, 3),
                "time_avg": round(time_avg, 3),
                "time_max": round(time_max, 3),
                "time_med": round(time_med, 3),
                "time_perc": round(time_perc, 3),
                "time_sum": round(time_sum, 3),
            }
        )

    result.sort(key=lambda res: res["time_sum"], reverse=True)
    return result


def fill_html_report(config: ConfigParser, filename: str, result_data: dict) -> bool:
    template = config.get("DEFAULT", "REPORT_TEMPLATE")
    report_file = "./{}/{}".format(config.get("DEFAULT", "REPORT_DIR"), filename)

    with open(template, mode="r") as template:
        with open(report_file, mode="w") as report:
            for line in template:
                if "$table_json" in line:
                    report.write(line.replace("$table_json", json.dumps(result_data)))
                else:
                    report.write(line)


def main(report_config) -> None:
    if not init_logging_config(level="DEBUG"):
        sys.exit("Check init_logging_config() usage!")

    last_log_file = get_the_last_log_file(report_config)
    if not last_log_file:
        sys.exit("Can't get last log file! Finishing script...")
    logging.debug("The last log file is - {}".format(last_log_file.filename))

    report_name = get_report_name(last_log_file.date)
    logging.debug("Result file name will be - {}".format(report_name))

    if check_report_exists(report_config.get("DEFAULT", "REPORT_DIR"), report_name):
        sys.exit("The report file ({}) already exists".format(report_name))

    log_data = parse_logs(last_log_file.filename)
    if not log_data:
        sys.exit(
            "There are too many errors in parsing! Check log file format - {}".format(
                last_log_file
            )
        )
    logging.info("Log file has been parsed successfully...")

    result = handle_log_data(log_data, report_config)
    logging.info("Log data has been processed successfully...")

    fill_html_report(report_config, report_name, result)
    logging.info("Log analyzer script has finished the work!")


if __name__ == "__main__":
    args = parse_arguments()
    if args.config_path and not os.path.exists(args.config_path):
        sys.exit("No such config file!")

    config = get_config_values(config, args.config_path)
    main(config)
