from apps.eservice.emails_handler import Email
from apps.eservice.providers.emails_provider import EmailsProvider


class SimpleMockEmailsProvider(EmailsProvider):
    @property
    def name(self) -> str:
        return "simple_mock"

    def send(self, email: Email) -> bool:
        return True


class BadMockEmailsProvider(EmailsProvider):
    @property
    def name(self) -> str:
        return "bad_mock"

    def send(self, email: Email) -> bool:
        return False
