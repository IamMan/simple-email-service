import time
from time import mktime

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, SmallInteger, and_

from apps.eservice.daos import EmailsDao
from apps.eservice.email_handler import EmailStatus, Email
from apps.helpers import db_call_global_retry
from .model import Base


class Emails(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    from_email = Column(String)
    recipients = Column(String)
    subject = Column(String)
    html = Column(String)
    created_at = Column(BigInteger)

    status = Column(SmallInteger)
    updated_at = Column(BigInteger)
    via = Column(String)
    message = Column(String)


class SqlAlchemyEmailsDao(EmailsDao):

    def __init__(self, session):
        self._session = session

    @staticmethod
    def _db_email_to_email(db_email: Emails):
        if db_email is None:
            return None
        return Email(id=db_email.id,
                     user_id=db_email.user_id,
                     from_email=db_email.from_email,
                     recipients=db_email.recipients,
                     subject=db_email.subject,
                     html=db_email.html,
                     # created_at=time.localtime(db_email.created_at),
                     created_at=db_email.created_at,
                     status=EmailStatus(db_email.status),
                     # updated_at=time.localtime(db_email.created_at),
                     updated_at=db_email.updated_at,
                     via=db_email.via,
                     message=db_email.message)

    def get_email(self, email_id) -> Email:
        db_email = self._session.query(Emails).get(email_id)
        return self._db_email_to_email(db_email)

    @db_call_global_retry
    def save_email(self, email) -> Email:

        ctime = mktime(time.gmtime())
        epoch_time = int(ctime)
        db_email = Emails(user_id=email.user_id,
                          from_email=email.from_email,
                          recipients=email.recipients,
                          subject=email.subject,
                          html=email.html,
                          status=EmailStatus.CREATED.value,
                          created_at=epoch_time,
                          updated_at=epoch_time)
        self._session.add(db_email)
        self._session.flush()

        email.id = db_email.id
        email.status = EmailStatus.CREATED
        email.created_at = ctime
        email.updated_at = ctime
        return email

    @db_call_global_retry
    def update_status_if_timestamp_after(self, email_id, status, event_timestamp):
        status_code = status.value
        self._session.query(Emails). \
            filter(and_(Emails.id == email_id, Emails.updated_at < event_timestamp)). \
            update({"status": status_code, "updated_at": event_timestamp})
