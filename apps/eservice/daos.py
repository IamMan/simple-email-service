import abc
import json
from enum import Enum


class EmailStatus(Enum):
    # Email created in service
    CREATED = 0
    # Accepted the request to send/forward the email and the message has placed in provider
    ACCEPTED = 1
    # Provider rejected the request to send/forward the email.
    REJECTED = 2
    # Email delivered
    DELIVERED = 3
    # Provider could not deliver the email to the recipient email server.
    FAILED = 4


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)


class Email(object):

    def __init__(self, user_id, from_email, recipients, subject, html,
                 created_at=None, status=None, updated_at=None, via=None, message=None, id=None):
        self.id = id
        self.user_id = user_id

        self.from_email = from_email
        self.recipients = recipients
        self.subject = subject
        self.html = html

        self.created_at = created_at
        self.status = status
        self.updated_at = updated_at
        self.via = via
        self.message = message

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class EmailsDao:

    @abc.abstractmethod
    def update_status_if_timestamp_after(self, email_id, status, event_timestamp):
        pass

    @abc.abstractmethod
    def save_email(self, email) -> Email:
        pass

    @abc.abstractmethod
    def get_email(self, email_id) -> Email:
        pass


class UsersDao:
    @abc.abstractmethod
    def get_user_id_by_access_key(self, api_key):
        pass


class DaoEncoder(json.JSONEncoder):
    def default(self, obj):
        return dir(obj)
