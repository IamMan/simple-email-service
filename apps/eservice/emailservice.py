import json
import logging
import os
from os.path import isfile, join
import sys

from lambdarest import lambda_handler
from apps.db.context import GlobalContext
from apps.eservice.emails_handler import EmailsHandler
from apps.eservice.api_doc_handler import ApiDocHandler
from apps.eservice.email_handler import EmailsHandler
from apps.helpers import wrap_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    stream=sys.stdout)
logger = logging.getLogger("EmailService")
logger.setLevel(logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

logger.info("EService initializing...")

global_cntxt = GlobalContext.create_context()


def apply_db_migration(cntxt):
    logger.info("Applying migration...")
    sql = join(os.getcwd(), 'sql')
    onlyfiles = [join(sql, f) for f in os.listdir(sql) if isfile(join(sql, f))]
    for path in onlyfiles:
        logger.info("Applying migration at path")
        with open(path, 'r') as f:
            stmt = f.read()
            cntxt.session.execute(stmt)
    logger.info("Migration finished")


api_doc_handler = ApiDocHandler()
emails_handler = EmailsHandler(global_cntxt.users_dao, global_cntxt.emails_dao, [])

logger.info("EService initialization finished...")


@lambda_handler.handle("get", path="/api-doc/*")
def swagger_doc(event, **kwargs):
    return wrap_event(api_doc_handler.handle, event)


@lambda_handler.handle("post", path="/emails")
def email_sent(event, **kwargs):
    return wrap_event(emails_handler.handle_create_email, event)


@lambda_handler.handle("get", path="/email/{email_id}")
def email_get(event):
    return wrap_event(emails_handler.handle_get_email, event)


@lambda_handler.handle("post", path="/email/{email_id}/send")
def email_send(event):
    return wrap_event(emails_handler.handle_send_email, event)


def handler(event, context=None):
    if event.get('type') == 'admin' and event.get('op') == 'db_migration':
        apply_db_migration(global_cntxt)
    else:
        logger.info(json.dumps(event, indent=4))
        response = lambda_handler(event)
        logger.info("{} {}".format(event.get("path"), response.get("statusCode")))
        return response
