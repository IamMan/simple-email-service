import os
from os.path import isfile, join

import pytest

from apps.db.context import GlobalContext
from apps.eservice.daos import Email, EmailStatus


@pytest.fixture(scope='module')
def context():

    cntxt = GlobalContext.create_context()

    am = os.environ.get("APPLY_MIGRATION")
    if am is not None:
        apply_db_migration(cntxt)

    print('Context prepared')
    yield cntxt
    print('Finished!')


def apply_db_migration(cntxt):
    onlyfiles = [join('../sql', f) for f in os.listdir('../sql') if isfile(join('../sql', f))]
    for path in onlyfiles:
        print(path + '\n')
        with open(path, 'r') as f:
            stmt = f.read()
            cntxt.session.execute(stmt)


class DbWithOneUser:

    def __init__(self, cntxt):
        self.cntxt = cntxt

    def clean_test_tables(self):
        self.cntxt.session.execute("truncate table emails, users RESTART IDENTITY")

    def create_test_user(self):
        self.cntxt.session.execute(
            "insert into public.users(login, passwordhash, apikey) values ('test_user', MD5('test_pass'), "
            "uuid_generate_v4())")

    def __enter__(self):
        self.clean_test_tables()
        self.create_test_user()

    def __exit__(self, type, value, traceback):
        self.clean_test_tables()


def test_sqlalchemy_dao_save_email(context):
    with DbWithOneUser(context):
        emails_dao = context.emails_dao
        email = Email(1, "test@test.test", "test3@test.test,test2@test.test", "test", "Test text")
        email = emails_dao.save_email(email)
        assert email.id is not None and email.id == 1
        assert email.status is not None and email.status == EmailStatus.CREATED
        assert email.created_at is not None


def test_sqlalchemy_dao_get(context):
    with DbWithOneUser(context):
        emails_dao = context.emails_dao
        email = Email(1, "test@test.test", "test3@test.test,test2@test.test", "test", "Test text")
        email_saved = emails_dao.save_email(email)
        emails_got = emails_dao.get_email(1, email_saved.id)
        assert email_saved == emails_got


def test_sqlalchemy_dao_update_status_after(context):
    with DbWithOneUser(context):
        emails_dao = context.emails_dao
        email = Email(1, "test@test.test", "test3@test.test,test2@test.test", "test", "Test text")
        email = emails_dao.save_email(email)

        updated_at = email.created_at + 100500
        emails_dao.update_status_and_message_if_timestamp_after(email.id, EmailStatus.ACCEPTED, updated_at, "updated")

        emails_got = emails_dao.get_email(1, email.id)
        assert emails_got.id is not None and email.id == 1
        assert emails_got.status is not None and emails_got.status == EmailStatus.ACCEPTED
        assert emails_got.created_at == email.created_at
        assert emails_got.updated_at == updated_at
