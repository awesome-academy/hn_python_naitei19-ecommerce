import os

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def int_or_none(x: str):
    """Convert a string to int. If false, return None."""
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def float_or_none(x: str):
    """Convert a string to float. If false, return None."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def send_email(subject, body, to, template=None, attachment=None, **context):
    body_html = render_to_string(
        os.path.join(settings.BASE_DIR, f'templates/email/{template}'),
        **context
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=to
    )
    message.mixed_subtype = 'related'
    message.attach_alternative(body_html, "text/html")
    message.attach(attachment)

    message.send(fail_silently=False)
