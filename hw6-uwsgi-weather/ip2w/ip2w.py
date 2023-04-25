import socket

def check_valid_ip(ip_addres: str) -> bool:
    try:
        socket.inet_aton(ip_addres)
        return "True"
    except socket.error:
        return "False"


def application(env, start_response):
    ip_address = env["REQUEST_URI"].replace("/ip2w/", "")
    response = check_valid_ip(ip_address)
    start_response("200 OK", [("Content-Type", "text/html")])
    return [bytes(response, encoding="utf-8")]
