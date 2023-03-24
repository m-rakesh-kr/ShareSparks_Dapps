from celery import shared_task
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import CustomUser


@shared_task()
def send_password_reset_mail(email, user_id):
    subject = 'Reset Password Email'
    email_from = 'from@example.com'
    recipient_list = [email]
    user = CustomUser.objects.get(id=user_id)
    reset_token = default_token_generator.make_token(user)
    u_id = urlsafe_base64_encode(force_bytes(user.id))
    reset_link = (
        f'http://127.0.0.1:8000/password-reset-confirm/{u_id}/{reset_token}'
    )
    context = {
        'reset_link': reset_link
    }
    message = render_to_string('users/email_template.html', context)
    email = EmailMessage(subject, message, email_from, recipient_list)
    email.content_subtype = 'html'  # Main content is now text/html
    email.send()
