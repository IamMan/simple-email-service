import json
import logging
import os

from sparkpost import SparkPost
from sparkpost.exceptions import SparkPostAPIException

from apps.eservice.daos import Email, EmailStatus
from apps.eservice.providers.emails_provider import EmailsProvider
from apps.helpers import LambdaEventWrapper, Response


def get_spark_api_from() -> str:
    api_from = os.environ.get("SPARKPOST_API_FROM")
    return api_from


def get_spark_api_is_sandbox() -> bool:
    is_sandbox = os.environ.get("SPARKPOST_API_IS_SANDBOX")
    return is_sandbox == "YES"


class SparkpostEmailsProvider(EmailsProvider):

    def __init__(self, sparkpost_from, sparkpost_is_sandbox) -> None:
        super().__init__()
        # SPARKPOST_API_KEY
        self.sp = SparkPost()
        self.sparkpost_from = sparkpost_from
        self.sparkpost_is_sandbox = sparkpost_is_sandbox
        self.logger = logging.getLogger("SparkpostEmailsProvider")
        self.logger.setLevel(logging.INFO)
        self.logger.info("SparkpostEmailsProvider initialized")

    @property
    def name(self) -> str:
        return "sparkpost"

    def send(self, email: Email) -> bool:
        assert email.id is not None
        try:
            response = self.sp.transmissions.send(
                use_sandbox=self.sparkpost_is_sandbox,
                recipients=email.recipients.split(', '),
                html=email.html,
                from_email='{} <{}>'.format(email.from_email, self.sparkpost_from),
                subject=email.subject,
                metadata={'email_id': email.id}
            )
        except SparkPostAPIException as e:
            self.logger.warning(str(e))
            return False
        print(response)
        return True


class SparkpostReceiverHandler:

    def __init__(self, emails_dao) -> None:
        super().__init__()
        # SPARKPOST_API_KEY
        self.emails_dao = emails_dao
        self.sp = SparkPost()
        self.logger = logging.getLogger("SparkpostReceiverHandler")
        self.logger.setLevel(logging.INFO)
        self.logger.info("SparkpostReceiverHandler initialized")

    def handle(self, event: LambdaEventWrapper) -> Response:
        try:
            webhook_payload = json.loads(event.get_body())
        except ValueError:
            self.logger.info("Malformed webhook payload json")
            return Response.make_response(406)

        self.process_event(webhook_payload)
        return Response.make_response(200)

    @staticmethod
    def get_event_type(event):
        return event.get('event')

    @staticmethod
    def get_timestamp(event):
        return event.get('timestamp')

    @staticmethod
    def get_meta(event):
        return event.get('rcpt_meta')

    @staticmethod
    def get_email_id(event):
        meta = SparkpostReceiverHandler.get_meta(event)
        if meta is None:
            return None
        return meta.get("email_id")

    @staticmethod
    def get_event(msys):
        return msys.get('message_event')

    def process_event(self, webhook):
        for msys in webhook:
            event = SparkpostReceiverHandler.get_event(msys)
            if event is None:
                self.logger.warning("Malformed event")
                continue

            email_id = SparkpostReceiverHandler.get_email_id(event)
            if email_id is None:
                self.logger.warning("Webhook without or bad email received")
                continue

            event_type = SparkpostReceiverHandler.get_event_type(event)
            timestamp = SparkpostReceiverHandler.get_timestamp(event)

            if event_type == 'delivery':
                status = EmailStatus.DELIVERED
                message = 'ok'
            else:
                if event == 'bounce':
                    status = EmailStatus.FAILED
                    message = None
                else:
                    status = EmailStatus.REJECTED
                    message = None

            self.emails_dao.update_status_and_message_if_timestamp_after(email_id, status, timestamp, message)


def create_sparkpost_receiver(emails_dao) -> SparkpostReceiverHandler:
    return SparkpostReceiverHandler(emails_dao)
