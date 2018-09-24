import hashlib
import hmac
import json
import logging
import os

import requests

from apps.eservice.daos import Email, EmailsDao, EmailStatus
from apps.eservice.providers.emails_provider import EmailsProvider
from apps.helpers import LambdaEventWrapper, Response


def get_api_key() -> str:
    api_key = os.environ.get("MAILGUN_API_KEY")
    return api_key


def get_api_url() -> str:
    api_url = os.environ.get("MAILGUN_API_URL")
    return api_url


def get_api_from() -> str:
    api_from = os.environ.get("MAILGUN_API_FROM")
    return api_from


class MailgunEmailsProvider(EmailsProvider):

    def __init__(self, mailgun_uri, mailgun_apikey, mailgun_email) -> None:
        super().__init__()
        self.mailgun_uri = mailgun_uri
        self.mailgun_apikey = mailgun_apikey
        self.mailgun_email = mailgun_email
        self.logger = logging.getLogger("MailgunEmailsProvider")
        self.logger.setLevel(logging.INFO)
        self.logger.info("MailgunEmailsProvider initialized")

    @property
    def name(self) -> str:
        return "mailgun"

    def send(self, email: Email) -> bool:
        assert email.id is not None

        response = requests.post(
            # "https://api.mailgun.net/v3/sandboxe728d383fab7400f89eed08d8d706781.mailgun.org/messages",
            self.mailgun_uri,
            # auth=("api", "bb8e4181228d51538104181eb543f6a9-0e6e8cad-abcebabe"),
            auth=("api", self.mailgun_apikey),
            # data={"from": "<postmaster@sandboxe728d383fab7400f89eed08d8d706781.mailgun.org>",
            data={
                "from": "{} <{}>".format(email.from_email, self.mailgun_email),
                "to": email.recipients.split(', '),
                "subject": email.subject,
                "html": email.html,
                "v:email_id": email.id})

        if response.status_code == 200:
            return True
        else:
            return False


def create_mailgun_provider() -> MailgunEmailsProvider:
    api_url = get_api_url()
    if api_url is None:
        raise ValueError("mailgun api key undefined")
    api_key = get_api_key()
    if api_key is None:
        raise ValueError("mailgun api url undefined")
    api_from = get_api_from()
    if api_from is None:
        raise ValueError("mailgun api from undefined")
    return MailgunEmailsProvider(api_url, api_key, api_from)


class MailgunReceiverHandler:
    def __init__(self, mailgun_apikey, emails_dao: EmailsDao) -> None:
        super().__init__()
        self.emails_dao = emails_dao
        self.mailgun_apikey = mailgun_apikey
        self.logger = logging.getLogger("MailgunReciver")
        self.logger.setLevel(logging.INFO)
        self.logger.info("MailgunReciver initialized")

    def verify(self, token, timestamp, signature):
        hmac_digest = hmac.new(key=self.mailgun_apikey.encode('utf-8'),
                               msg='{}{}'.format(timestamp, token).encode('utf-8'),
                               digestmod=hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature.encode('utf-8'), hmac_digest.encode('utf-8'))

    def handle(self, event: LambdaEventWrapper) -> Response:
        try:
            webhook_payload = json.loads(event.get_body())
        except ValueError:
            self.logger.info("Malformed webhook payload json")
            return Response.make_response(406)

        signature = webhook_payload.get("signature")
        if signature is not None:
            verify_results = self.verify(signature.get("token"), signature.get("timestamp"), signature.get("signature"))
        else:
            self.logger.info("Signature not found in webhook")
            return Response.make_response(406)

        if not verify_results:
            self.logger.info("Webhook not verified")
            return Response.make_response(406)

        event_data = webhook_payload.get("event-data")
        self.process_event_data(event_data)

        return Response.make_response(200)

    @staticmethod
    def get_user_variables(event_data):
        return event_data.get("user-variables")

    @staticmethod
    def get_timestamp(event_data):
        return int(event_data.get("timestamp"))

    @staticmethod
    def get_delivery_status(event_data):
        return event_data.get("delivery-status")

    @staticmethod
    def get_event(event_data):
        return event_data.get("event")

    @staticmethod
    def get_email_id(event_data):
        uv = MailgunReceiverHandler.get_user_variables(event_data)
        if uv is None:
            return None
        try:
            email_id = uv.get("email_id")
        except Exception:
            email_id = None
        return email_id

    def process_event_data(self, event_data):
        assert event_data is not None

        email_id = MailgunReceiverHandler.get_email_id(event_data)
        if email_id is None:
            self.logger.warning("Webhook without or bad email received")
            return

        timestamp = MailgunReceiverHandler.get_timestamp(event_data)
        event = MailgunReceiverHandler.get_event(event_data)
        delivery_status = MailgunReceiverHandler.get_delivery_status(event_data)

        if event == 'delivered':
            status = EmailStatus.DELIVERED
            message = 'ok'
        else:
            if event == 'failed':
                status = EmailStatus.FAILED
                message = delivery_status.get('description')
            else:
                status = EmailStatus.REJECTED
                message = delivery_status.get('description')

        self.emails_dao.update_status_and_message_if_timestamp_after(email_id, status, timestamp, message)


def create_mailgun_receive_handler(emails_dao) -> MailgunReceiverHandler:
    api_key = get_api_key()
    if api_key is None:
        raise ValueError("mailgun api url undefined")
    return MailgunReceiverHandler(api_key, emails_dao)
