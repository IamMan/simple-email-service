import json
import logging

from apps.eservice.daos import UsersDao, EmailsDao, Email, EmailStatus, EnumEncoder
from apps.helpers import LambdaEventWrapper, Response, ExceptionWithCode, generate_unauthorized_message


class EmailsHandler():
    def __init__(self, users_dao: UsersDao, emails_dao: EmailsDao, emails_providers: list):
        self.users_dao = users_dao
        self.emails_dao = emails_dao
        self.emails_providers = emails_providers
        self._logger = logging.getLogger("EmailsHandler")

    def validate_api_key(self, params):
        api_key = params.get("api_key")
        if api_key is None:
            raise ExceptionWithCode(
                401,
                generate_unauthorized_message()
            )
        user_id = self.users_dao.get_user_id_by_access_key(api_key)
        if user_id is None:
            raise ExceptionWithCode(
                401,
                generate_unauthorized_message()
            )
        return user_id

    def initialize_email(self, event) -> Email:
        user_id = self.validate_api_key(event.get_headers())
        email_body = json.loads(event.get_body())
        from_email = Response.get_parameter_or_throw_exception("from_email", email_body)
        recipients = Response.get_parameter_or_throw_exception("recipients", email_body)
        subject = Response.get_parameter_or_throw_exception("subject", email_body)
        html = Response.get_parameter_or_throw_exception("html", email_body)

        return Email(user_id, from_email, recipients, subject, html)

    def save_email(self, email) -> Email:
        assert email.user_id is not None
        assert email.from_email is not None
        assert email.recipients is not None
        assert email.subject is not None
        assert email.html is not None

        return self.emails_dao.save_email(email)

    def send_email(self, email) -> Email:
        assert email.id is not None
        assert email.status == EmailStatus.CREATED

        for provider in self.emails_providers:
            try:
                email = provider.send(email)
            except Exception:
                self._logger.exception("Provider {} raise exception".format(provider.name))
            finally:
                if email.via == provider.name:
                    return email
        return email

    def handle_sand_email(self, event: LambdaEventWrapper) -> Response:
        email = self.initialize_email(event)
        email = self.save_email(email)
        email = self.send_email(email)
        return Response.make_response(200, json.dumps(email.__dict__, indent=4, cls=EnumEncoder))


