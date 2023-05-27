import argparse
import logging
import socket
import traceback
from typing import Optional

DOCUMENT_ROOT = "www"
MAX_NUM_CONNECTIONS = 5


def handle_request(connection, address, document_root):
    response_data = "HTTP/1.0 200 OK\n\nHello {}".format(address)
    connection.sendall(response_data.encode())
    connection.close()


class HTTPServer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        document_root: str = DOCUMENT_ROOT,
        max_num_connections: str = MAX_NUM_CONNECTIONS,
    ) -> None:
        self.host = host
        self.port = port
        self.document_root = document_root
        self.max_num_connections = max_num_connections

    def run(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_num_connections)
        except socket.error as e:
            raise RuntimeError(e)

    def serve_forever(self) -> None:
        while True:
            client_connection, client_address = self.socket.accept()
            logging.debug("Obtain request from {}".format(client_address))
            handle_request(
                client_connection,
                client_address,
                self.document_root,
            )


def run_server(host: str, port: int, document_root: str):
    logging.info("Starting server at http://{}:{}".format(host, port))
    server = HTTPServer(host, port, document_root)
    server.run()
    server.serve_forever()


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

    parser.add_argument("-s", "--host", type=str, default="127.0.0.1", help="Hostname")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port number")
    parser.add_argument(
        "-r",
        "--root",
        type=str,
        default=DOCUMENT_ROOT,
        help="Files root directory (DOCUMENT_ROOT)",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Show debug messages"
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    init_logging_config()
    run_server(args.host, args.port, args.root)
