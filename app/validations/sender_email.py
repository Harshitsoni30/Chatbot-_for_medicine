import random
from email.message import EmailMessage
import aiosmtplib


def generate_otp():
    return str(random.randint(1000, 9999))

# Setup for sending emails to users
async def send_otp_email(email_to: str, otp: str):
    message = EmailMessage()
    message["From"] = "hsoni2841@gmail.com"
    message["To"] = email_to
    message["Subject"] = "Your OTP Code"
    message.set_content(f"Your OTP code is: {otp}")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="hsoni2841@gmail.com",
        password="riny zbwr fvkc whfa",  
    )
