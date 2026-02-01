from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER


def send_quick_mail(subject, message, to_email):
    from_email = EMAIL_HOST_USER
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_email],
        html_message=f"{message}",
        fail_silently=False,
    )