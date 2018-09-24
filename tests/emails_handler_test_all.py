import json

from apps.eservice.daos import EmailStatus
from apps.eservice.emails_handler import EmailsHandler
from apps.helpers import LambdaEventWrapper, wrap_event
from staff.test_emails_dao import MockUsersDao, MockEmailsDao
from staff.test_emails_providers import SimpleMockEmailsProvider, BadMockEmailsProvider


def assemble_request(path, path_params=None, query_params=None, headers=None, body=None, method='GET'):
    path_params = path_params or {}
    query_params = query_params or {}
    headers = headers or {}

    return {
        "httpMethod": method,
        "resource": path,
        "pathParameters": path_params,
        "queryStringParameters": query_params,
        "headers": headers,
        "body": body,
    }


def test_email_create_simple():
    emails_handler = EmailsHandler(MockUsersDao(), MockEmailsDao(), [SimpleMockEmailsProvider()])

    event = assemble_request(
        "/emails",
        method="POST",
        headers={"api_key": "test_api_key"},
        body="{\"from_email\":\"test@test.test\",\"recipients\":\"test@test.test,test1@test.test,test2@test.test\","
             "\"subject\":\"test email\",\"html\":\"Text of the email\"} "
    )
    event = LambdaEventWrapper(event)
    response = emails_handler.handle_create_email(event)
    code = response.status_code
    assert code is not None and code == 200
    email = json.loads(response.body)
    assert email.get("id") is not None
    assert email.get("status") is not None and email.get("status") == EmailStatus.CREATED.name


def test_email_sent_when_one_provider_unavailable():
    emails_handler = EmailsHandler(MockUsersDao(), MockEmailsDao(), [BadMockEmailsProvider(), SimpleMockEmailsProvider()])

    event = assemble_request(
        "/email/1/send",
        method="POST",
        headers={"api_key": "test_api_key"},
        path_params={"email_id": 1}
    )

    response = wrap_event(emails_handler.handle_send_email, event)

    code = response.status_code
    assert code is not None and code == 200
    email = json.loads(response.body)
    assert email.get("id") is not None
    assert email.get("status") is not None and email.get("status") == EmailStatus.ACCEPTED.name


def test_email_sent_when_all_provider_unavailable():
    emails_handler = EmailsHandler(MockUsersDao(), MockEmailsDao(), [BadMockEmailsProvider(), BadMockEmailsProvider()])

    event = assemble_request(
        "/email/1/send",
        method="POST",
        headers={"api_key": "test_api_key"},
        path_params={"email_id": 1}
    )

    response = wrap_event(emails_handler.handle_send_email, event)

    code = response.status_code
    assert code is not None and code == 400

