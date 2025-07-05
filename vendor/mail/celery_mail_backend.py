from django.core.mail.backends.base import BaseEmailBackend

from core.tasks import send_mail_task


class CeleryEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        for email_message in email_messages:
            self._send(email_message)

    def _send(self, email_message):
        """A helper method that does the actual sending."""

        if not email_message.recipients():
            return False

        mail_kwargs = {
            "subject": email_message.subject,
            "message": email_message.body,
            "from_email": email_message.from_email,
            "recipient_list": email_message.recipients(),
            "fail_silently": False,
            "auth_user": None,
            "auth_password": None,
            "connection": None,
            "html_message": email_message.html,
        }

        send_mail_task.delay(**mail_kwargs)
