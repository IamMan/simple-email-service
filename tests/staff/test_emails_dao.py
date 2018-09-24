import time
from time import mktime


from apps.eservice.daos import UsersDao, EmailsDao
from apps.eservice.emails_handler import Email, EmailStatus


class MockUsersDao(UsersDao):
    def get_user_id_by_access_key(self, api_key):
        return 1


class MockEmailsDao(EmailsDao):

    def get_email(self, user_id, email_id) -> Email:
        email = Email(user_id, "test@email", "test1@test.test, test2@test.test", "test", "test text")
        email.id = email_id
        email.status = EmailStatus.CREATED
        email.updated_at = mktime(time.gmtime())
        email.created_at = mktime(time.gmtime())
        return email

    def __init__(self) -> None:
        self._current_email_id = 1

    def update_status_if_timestamp_after(self, email_id, status, event_timestamp):
        pass

    def save_email(self, email) -> Email:
        ctime = mktime(time.gmtime())
        email.id = self._current_email_id + 1
        self._current_email_id = self._current_email_id + 1
        email.status = EmailStatus.CREATED
        email.created_at = ctime
        email.updated_at = ctime
        return email
