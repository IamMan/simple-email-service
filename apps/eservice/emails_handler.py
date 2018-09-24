import json
import logging
import time

from apps.eservice.daos import UsersDao, EmailsDao, Email, EmailStatus, EnumEncoder
from apps.helpers import LambdaEventWrapper, Response, ExceptionWithCode, generate_unauthorized_message, \
    get_parameter_or_throw_exception


class EmailsHandler:
    def __init__(self, users_dao: UsersDao, emails_dao: EmailsDao, emails_providers: list):
        self.users_dao = users_dao
        self.emails_dao = emails_dao
        self.emails_providers = emails_providers
        self._logger = logging.getLogger("EmailsHandler")

    def validate_api_key(self, params):
        api_key = params.get("api_key")
        if api_key is None:
            raise ExceptionWithCode(401, generate_unauthorized_message())
        user_id = self.users_dao.get_user_id_by_access_key(api_key)
        if user_id is None:
            raise ExceptionWithCode(401, generate_unauthorized_message())
        return user_id[0]

    @staticmethod
    def initialize_email(user_id, event) -> Email:
        try:
            email_body = json.loads(event.get_body())
        except ValueError:
            raise ExceptionWithCode(400, "Malformed email payload json")

        from_email = get_parameter_or_throw_exception("from_email", email_body)
        recipients = get_parameter_or_throw_exception("recipients", email_body)
        subject = get_parameter_or_throw_exception("subject", email_body)
        html = get_parameter_or_throw_exception("html", email_body)

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

        timestamp = int(time.mktime(time.gmtime()))
        for provider in self.emails_providers:
            try:
                is_accepted = provider.send(email)
                if is_accepted:
                    self.emails_dao.update_via(email.id, provider.name)

                    self.emails_dao.update_status_and_message_if_timestamp_after(email.id, EmailStatus.ACCEPTED,
                                                                                 timestamp, None)
                    email.via = provider.name
                    email.status = EmailStatus.ACCEPTED
                    email.updated_at = timestamp
                    return email
            except Exception:
                self._logger.exception("Provider {} raise exception".format(provider.name))

        raise ExceptionWithCode(400, "All emails providers temporarily unavailable")

    def handle_create_email(self, event: LambdaEventWrapper) -> Response:
        user_id = self.validate_api_key(event.get_headers())
        email = self.initialize_email(user_id, event)
        email = self.save_email(email)

        return Response.make_response(200, json.dumps(email.__dict__, indent=4, cls=EnumEncoder))

    @staticmethod
    def raise_email_not_found(email_id):
        raise ExceptionWithCode(404, "Email with {} id not found".format(email_id))

    def handle_send_email(self, event: LambdaEventWrapper) -> Response:
        user_id = self.validate_api_key(event.get_headers())
        email_id = get_parameter_or_throw_exception("email_id", event.get_path_params())

        email = self.emails_dao.get_email(user_id, email_id)
        if email is None:
            EmailsHandler.raise_email_not_found(email_id)
        if email.status != EmailStatus.CREATED:
            raise ExceptionWithCode(400, "Email have been already sent")

        email = self.send_email(email)
        return Response.make_response(200, json.dumps(email.__dict__, indent=4, cls=EnumEncoder))

    def handle_get_email(self, event: LambdaEventWrapper) -> Response:
        user_id = self.validate_api_key(event.get_headers())

        email_id = get_parameter_or_throw_exception("email_id", event.get_path_params())
        email = self.emails_dao.get_email(user_id, email_id)
        if email is None:
            EmailsHandler.raise_email_not_found(email_id)

        return Response.make_response(200, json.dumps(email.__dict__, indent=4, cls=EnumEncoder))


