import os

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.db.emails_dao import SqlAlchemyEmailsDao
from apps.db.users_dao import SqlAlchemyUsersDao


class GlobalContext:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=self.engine, autocommit=True)
        self.session = Session()
        self.users_dao = SqlAlchemyUsersDao(self.session)
        self.emails_dao = SqlAlchemyEmailsDao(self.session)

    @staticmethod
    def get_password() -> str:
        password = os.environ.get("DB_PASSWORD")
        ssm_path = os.environ.get("PASSWORD_SSM_PATH")
        if password is None and ssm_path:
            ssm_client = boto3.client('ssm')
            param: dict = ssm_client.get_parameter(Name=ssm_path, WithDecryption=True)
            password = param["Parameter"]["Value"]
        return password

    @staticmethod
    def get_db_url() -> str:
        db_url = os.environ.get("DB_URL")
        return db_url

    @staticmethod
    def create_context(db_password=None, db_url=None):
        password = db_password or GlobalContext.get_password()
        odbc_url = db_url or GlobalContext.get_db_url().format(password=password)
        return GlobalContext(odbc_url)
