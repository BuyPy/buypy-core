from django.core.mail import get_connection, send_mail
from rest_framework.settings import settings


def send_mail_task(**kwargs):
    connection = get_connection(backend=settings.TASK_EMAIL_BACKEND,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD)
    kwargs.update({"connection": connection})

    result = send_mail(**kwargs)

    return result
