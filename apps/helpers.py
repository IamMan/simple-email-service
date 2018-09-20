import json
import logging
from typing import Dict

import lambdarest
from sqlalchemy.exc import OperationalError
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type, stop_after_delay, before_sleep_log


class Response(lambdarest.Response):
    def __init__(self, body=None, status_code=None, headers=None, is_base64=False):
        self.body = body
        self.status_code = status_code
        self.headers = headers
        self.is_base64 = is_base64

    def to_json(self):
        return {
            "statusCode": self.status_code or 200,
            "body": self.body,
            "headers": self.headers or {},
            "isBase64Encoded": self.is_base64
        }

    @staticmethod
    def make_response(code: int, body=None, is_base64=False, headers=None):
        return Response(body, code, headers, is_base64)

    @staticmethod
    def make_response_with_message(code: int, msg: str) -> lambdarest.Response:
        return Response.make_response(code, json.dumps({"message": msg, "code": code}, indent=4))

    @staticmethod
    def make_500() -> lambdarest.Response:
        return Response.make_response_with_message(500, "Internal Server Error")

    @staticmethod
    def make_ok(body=None):
        return Response.make_response(200, body)

    @staticmethod
    def make_ok_base64(body):
        return Response.make_response(200, body, is_base64=True)

    @staticmethod
    def get_parameter_or_throw_exception(key, params):
        value = params.get(key) or None
        if value is None:
            raise ExceptionWithCode(
                401,
                generate_missed_field_message(key)
            )
        return value


def generate_unauthorized_message():
    return "Unauthorized"


def generate_missed_field_message(field):
    return "Missed '{}'".format(field)


def generate_unknown_message(type, was, valid):
    return "Unknown {} '{}', should be one of {}".format(type, was, valid)


class LambdaEventWrapper:
    def __init__(self, event):
        self.event = event

    def get_query_params(self) -> Dict:
        return self.event.get("queryStringParameters") or {}

    def get_path_params(self) -> Dict:
        return self.event.get("pathParameters") or {}

    def get_headers(self) -> Dict:
        return self.event.get("headers") or {}

    def get_body(self) -> Dict:
        return self.event.get("body") or {}


db_call_global_retry = retry(retry=retry_if_exception_type(OperationalError),
                             wait=wait_fixed(2),
                             stop=(stop_after_attempt(3) | stop_after_delay(20)),
                             before_sleep=before_sleep_log(logging, logging.WARN),
                             reraise=True)


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


class ExceptionWithCode(Exception):
    def __init__(self, code, text, *args):
        super(ExceptionWithCode, self).__init__(text, *args)
        self.text = text
        self.code = code



