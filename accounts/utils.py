# # accounts/utils.py
# import pyotp
# from django.conf import settings
# from django.core.mail import send_mail
# from django.utils import timezone
# import time

# # A helper to generate a TOTP secret for each email or use a site-wide secret.
# # We'll keep it simple: derive a secret from a site secret + email.

# SITE_OTP_SECRET = getattr(settings, 'SITE_OTP_SECRET', 'CHANGE_THIS_TO_A_SECURE_RANDOM_STRING')
# TOTP_INTERVAL = 300  # seconds (5 minutes) - adjust as needed


# def _derive_secret(email: str) -> str:
#     # Derive a per-email secret deterministically so we don't have to store secrets
#     # Note: for maximum security, you could store per-user secrets in DB.
#     key = (SITE_OTP_SECRET + email).encode()
#     # base32 encode deterministically
#     import hashlib, base64
#     digest = hashlib.sha256(key).digest()
#     return base64.b32encode(digest).decode('utf-8')


# def generate_totp(email: str) -> str:
#     secret = _derive_secret(email)
#     totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL, digits=6)
#     return totp.now()


# def verify_totp(email: str, code: str) -> bool:
#     secret = _derive_secret(email)
#     totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL, digits=6)
#     try:
#         return totp.verify(code, valid_window=1)
#     except Exception:
#         return False


# def send_otp_email(email: str, code: str, purpose: str = 'verification') -> None:
#     subject = f'Your {purpose} code'
#     message = f'Your {purpose} code is: {code}\nIt will expire in {TOTP_INTERVAL // 60} minutes.'
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import PasswordHistory


def send_otp_email(user, otp, purpose='verification'):
    subject = f"Your {purpose.replace('_', ' ').title()} Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]

    context = {
        "user": user,
        "code": otp.code,
        "expires_in": (otp.expires_at - otp.created_at).seconds // 60,
        "purpose": purpose.replace('_', ' ').title()
    }

    text_content = render_to_string("emails/otp_email.txt", context)
    html_content = render_to_string("emails/otp_email.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()




def store_password_history(user):
    # Save current password hash
    PasswordHistory.objects.create(user=user, password=user.password)

    # Keep only last 5 entries
    history = PasswordHistory.objects.filter(user=user).order_by("-created_at")
    if history.count() > 5:
        # delete older ones
        for old in history[5:]:
            old.delete()
