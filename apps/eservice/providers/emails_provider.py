import abc

from apps.eservice.emails_handler import Email


class EmailsProvider:

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def send(self, email: Email) -> bool:
        pass