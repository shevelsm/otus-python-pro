import json
import datetime
import logging
import hashlib
import re
from typing import Any, List, Optional, Union
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

from scoring import get_interests, get_score


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
EMPTY_VALUES = ("", [], (), {})
PENSION_AGE = 65


email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
phone_pattern = re.compile(r"7(\d{10})")


class Field:
    def __init__(
        self, required: Optional[bool] = False, nullable: Optional[bool] = False
    ) -> None:
        self.required = required
        self.nullable = nullable

    def validate(self, value: Any) -> Any:
        if self.required and value is None:
            raise ValueError("{} field is required!".format(self.__class__.__name__))
        if not self.nullable and value in EMPTY_VALUES:
            raise ValueError("{} field is not nullable".format(self.__class__.__name__))
        return value


class CharField(Field):
    def validate(self, value: str) -> str:
        super().validate(value)
        if not isinstance(value, str):
            raise TypeError("The field must be a string")
        return value


class ArgumentsField(Field):
    def validate(self, value: dict) -> dict:
        super().validate(value)
        if not isinstance(value, dict):
            raise TypeError("The field must be a dict")
        return value


class EmailField(CharField):
    def validate(self, value: str) -> str:
        super().validate(value)
        if not re.match(email_pattern, value):
            raise ValueError("The email address isn't correct")
        return value


class PhoneField(Field):
    def validate(self, value: Union[int, str]) -> str:
        value = str(value)
        super().validate(value)
        if not re.match(phone_pattern, value):
            raise ValueError(
                "The phone number isn't correct (should start with 7 and has length 11)"
            )
        return value


class DateField(CharField):
    def validate(self, value: str) -> str:
        super().validate(value)
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Incorrect date! The date format is %d.%m.%Y ")
        return value


class BirthDayField(DateField):
    def validate(self, value: str) -> str:
        super().validate(value)
        date = datetime.datetime.strptime(value, "%d.%m.%Y")
        if datetime.datetime.now().year - date.year > PENSION_AGE:
            raise ValueError(
                "The phone number isn't correct (should start with 7 and has length 11)"
            )
        return value


class GenderField(Field):
    def validate(self, value: int) -> int:
        super().validate(value)
        if not isinstance(value, int) or value not in GENDERS:
            raise ValueError("The gender field must be an integer value - 0, 1 or 2")
        return value


class ClientIDsField(Field):
    def validate(self, value: List[int]) -> List[int]:
        super().validate(value)
        if not isinstance(value, list):
            raise ValueError("The gender field should be list")
        for item in value:
            if not isinstance(item, int):
                raise ValueError("The client_ids field should be list of integers")
        return value


class RequestFields(type):
    def __new__(meta, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        attrs["_fields"] = fields
        return type.__new__(meta, name, bases, attrs)


class Request(metaclass=RequestFields):
    def __init__(self, **kwargs):
        for attribute in self._fields:
            value = kwargs.get(attribute)
            setattr(self, attribute, value)

    def validate(self):
        for attribute, field in self._fields.items():
            value = getattr(self, attribute)
            if value is not None or field.required:
                field.validate(value)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(MethodRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(MethodRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    @property
    def validate_personal_fields(self):
        if (
            (self.phone and self.email)
            or (self.first_name and self.last_name)
            or (self.birthday and self.gender in GENDERS)
        ):
            return True
        return False

    @property
    def has(self):
        return ["email", "phone"]


def check_auth(request):
    if request.is_admin:
        msg = datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
        digest = hashlib.sha512(msg.encode("UTF-8")).hexdigest()
    else:
        msg = request.account + request.login + SALT
        digest = hashlib.sha512(msg.encode("UTF-8")).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(request, context, store):
    context["has"] = request.arguments
    if request.is_admin:
        return {"score": 42}, OK

    try:
        r = OnlineScoreRequest(**request.arguments)
        r.validate()
    except (ValueError, TypeError) as err:
        error = {"code": INVALID_REQUEST, "error": str(err)}
        return error, INVALID_REQUEST

    if not r.validate_personal_fields:
        return {
            "code": INVALID_REQUEST,
            "error": "At least one pair of fields must be defined (phone + email) or (first_name  + last_name ) or (birthday + gender)",
        }, INVALID_REQUEST

    context["has"] = list(request.arguments.keys())

    score = get_score(
        store=store,
        phone=r.phone,
        email=r.email,
        birthday=r.birthday,
        gender=r.gender,
        first_name=r.first_name,
        last_name=r.last_name,
    )
    return {"score": score}, OK


def clients_interests_handler(request, context, store):
    try:
        r = ClientsInterestsRequest(**request.arguments)
        r.validate()
    except (ValueError, TypeError) as err:
        error = {"code": INVALID_REQUEST, "error": str(err)}
        return error, INVALID_REQUEST

    context["nclients"] = len(r.client_ids)

    interests = {}
    for client_id in r.client_ids:
        interests[client_id] = get_interests(store, client_id)
    return interests, OK


def method_handler(request, context, store):
    response, code = None, None
    method = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler,
    }
    try:
        r = MethodRequest(**request.get("body"))
        r.validate()
    except ValueError as err:
        return {"code": INVALID_REQUEST, "error": str(err)}, INVALID_REQUEST

    if not r.method:
        return {"code": INVALID_REQUEST, "error": "INVALID_REQUEST"}, INVALID_REQUEST

    if not check_auth(r):
        return None, FORBIDDEN

    response, code = method[r.method](r, context, store)
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    logging.debug("MainHTTPHandler")
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
