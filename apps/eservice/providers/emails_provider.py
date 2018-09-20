import abc

from apps.eservice.email_handler import Email


class EmailsProvider:

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def send(self, email: Email) -> Email:
        pass