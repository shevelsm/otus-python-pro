import argparse
from datetime import datetime
import logging
import mimetypes
import multiprocessing
import os
import socket
import traceback
from typing import Optional
from urllib.parse import unquote, urlparse

HTTP_PROTOCOL = "HTTP/1.1"
DOCUMENT_ROOT = "www"
MAX_NUM_CONNECTIONS = 5
CHUNK_SIZE = 1024
MAX_REQUEST_SIZE = 8192
HEADER_END_INDICATOR = "\r\n\r\n"

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
RESPONSE_CODES = {
    HTTP_200_OK: "OK",
    HTTP_400_BAD_REQUEST: "Bad Request",
    HTTP_403_FORBIDDEN: "Forbidden",
    HTTP_404_NOT_FOUND: "Not Found",
    HTTP_405_METHOD_NOT_ALLOWED: "Method Not Allowed",
}


class HTTPRequest:
    methods = ("GET", "HEAD")

    def __init__(self, document_root):
        self.document_root = document_root

    def parse(self, request_data):
        lines = request_data.split("\r\n")
        try:
            method, url, version = lines[0].split()
            method = method.upper()
        except ValueError:
            return HTTP_400_BAD_REQUEST, "?", "?", {}

        headers = {}
        for line in lines[1:]:
            if not line.split():
                break
            k, v = line.split(":", 1)
            headers[k.lower()] = v.strip()

        if method not in self.methods:
            return HTTP_405_METHOD_NOT_ALLOWED, method, url, headers

        code, path = self.parse_url(url)

        return code, method, path, headers

    def parse_url(self, url):
        parsed_path = unquote(urlparse(url).path)
        path = self.document_root + os.path.abspath(parsed_path)

        is_directory = os.path.isdir(path)
        if is_directory:
            if not path.endswith("/"):
                path += "/"
            path = os.path.join(path, "index.html")

        if not is_directory and parsed_path.endswith("/"):
            return HTTP_404_NOT_FOUND, path
        if path.endswith("/") or not os.path.isfile(path):
            return HTTP_404_NOT_FOUND, path

        return HTTP_200_OK, path


class HTTPResponse:
    def __init__(self, code, method, path, request_headers):
        self.code = code
        self.method = method
        self.path = path
        self.request_headers = request_headers

    def process(self):
        file_size = 0
        content_type = "text/plain"
        body = b""
        if self.code == HTTP_200_OK:
            file_size = self.request_headers.get(
                "content-length", os.path.getsize(self.path)
            )
            if self.method == "GET":
                content_type = mimetypes.guess_type(self.path)[0]
                with open(self.path, "rb") as file:
                    body = file.read(file_size)

        first_line = "{} {} {}".format(
            HTTP_PROTOCOL, self.code, RESPONSE_CODES[self.code]
        )
        headers = {
            "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Server": "Python-edu-server/0.1.0",
            "Connection": "close",
            "Content-Length": file_size,
            "Content-Type": content_type,
        }
        headers = "\r\n".join("{}: {}".format(k, v) for k, v in headers.items())
        response = (
            "{}\r\n{}{}".format(first_line, headers, HEADER_END_INDICATOR).encode()
            + body
        )
        return response


def receive(connection):
    fragments = []
    while True:
        chunk = connection.recv(CHUNK_SIZE).decode()
        if not chunk:
            raise ConnectionError
        if (
            not chunk
            or HEADER_END_INDICATOR in chunk
            or len(fragments) * CHUNK_SIZE >= MAX_REQUEST_SIZE
        ):
            fragments.append(chunk)
            break
        fragments.append(chunk)
    request = "".join(fragments)
    logging.debug("Final request is:\n{}".format(request))
    return request


def handle_request(
    connection: socket.socket, address: tuple, document_root: str
) -> None:
    try:
        request_data = receive(connection)
        request = HTTPRequest(document_root)
        code, method, path, headers = request.parse(request_data)
        response = HTTPResponse(code, method, path, headers)
        response_data = response.process()

        logging.info('"{} {} {}" {}'.format(method, path, HTTP_PROTOCOL, code))
        connection.sendall(response_data)
    except:
        logging.exception("Error while sending response to {}".format(address))
    finally:
        logging.debug("Closing socket for {}".format(address))
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


def run_server(host: str, port: int, workers: int, document_root: str):
    logging.info(
        "Starting server at http://{}:{} with root dir - {}".format(
            host, port, document_root
        )
    )
    server = HTTPServer(host, port, document_root)
    server.run()

    processes = []
    try:
        for _ in range(workers):
            process = multiprocessing.Process(target=server.serve_forever)
            processes.append(process)
            process.start()
            logging.debug("Worker with id {} was started".format(process.pid))
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            if process:
                process.terminate()
                logging.debug("Worker with id {} was terminated".format(process.pid))


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
        "-w", "--workers", type=int, default=1, help="Number of workers"
    )
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
    if args.debug:
        init_logging_config(level="DEBUG")
    else:
        init_logging_config(level="INFO")
    run_server(args.host, args.port, args.workers, args.root)
