import argparse
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic http server")

    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="Path to a config file",
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    init_logging_config()
    args = parse_arguments()
