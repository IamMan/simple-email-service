from sqlalchemy import Column, Integer, String

from apps.eservice.daos import UsersDao
from apps.helpers import db_call_global_retry
from .model import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    passwordHash = Column(String)
    apikey = Column(String)


class SqlAlchemyUsersDao(UsersDao):
    def __init__(self, session):
        self._session = session

    @db_call_global_retry
    def get_user_id_by_access_key(self, api_key):
        return self._session.query(Users.id).filter(Users.apikey == api_key).first()
