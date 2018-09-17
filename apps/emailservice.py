import logging
import sys

from lambdarest import lambda_handler

from .api_doc_handler import ApiDocHandler
from .helpers import LambdaEventWrapper, ExceptionWithCode, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    stream=sys.stdout)
logger = logging.getLogger("GlobalLogger")
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


api_doc_handler = ApiDocHandler()


def wrap_event(f, e):
    try:
        return f(LambdaEventWrapper(e))
    except ExceptionWithCode as r:
        return Response.make_response_with_message(r.code, r.text)
    except Exception:
        logger.exception(f"500 in {f.__name__}")
        return Response.make_response_with_message(500, "Internal Server Error")


@lambda_handler.handle("get", path="/api-docs/*")
def swagger_doc(event, **kwargs):
    return wrap_event(api_doc_handler.handle, event)


def handler(event, context=None):
    return lambda_handler(event)
