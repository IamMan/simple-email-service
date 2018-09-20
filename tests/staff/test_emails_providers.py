import time
from time import mktime

from apps.eservice.daos import EmailStatus
from apps.eservice.email_handler import Email
from apps.eservice.providers.emails_provider import EmailsProvider
from apps.helpers import ExceptionWithCode


class SimpleMockEmailsProvider(EmailsProvider):
    @property
    def name(self) -> str:
        return "simple_mock"

    def send(self, email: Email) -> Email:
        email.via = self.name
        email.status = EmailStatus.ACCEPTED
        email.updated_at = mktime(time.gmtime())
        return email


class BadMockEmailsProvider(EmailsProvider):
    @property
    def name(self) -> str:
        return "bad_mock"

    def send(self, email: Email) -> Email:
        raise ExceptionWithCode(423, "Limit exceeded")
