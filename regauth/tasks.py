
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_registration_email(user_email):
    send_mail(
        'Welcome to Our Site',
        'Thank you for registering on our site.',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
