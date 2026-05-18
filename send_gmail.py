#!/usr/bin/env python3
"""
Gmail SMTP sender for 5 Minūtes Latvijā.
Uses Gmail App Password (not your real password).
"""

import os
import hmac
import hashlib
import base64
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_single(subject: str, html_content: str, to_email: str) -> bool:
    """Send one email with a personal unsubscribe link. Returns True on success."""
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_app_password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"5 Minūtes Latvijā <{gmail_address}>"
            msg["To"] = to_email

            # List-Unsubscribe header — shown by Gmail / Apple Mail natively
            unsub_base = os.environ.get("UNSUB_BASE_URL", "").rstrip("/")
            if unsub_base:
                secret = os.environ.get("UNSUB_SECRET", "change-this-secret")
                email_b64 = base64.urlsafe_b64encode(to_email.encode()).decode()
                sig = hmac.new(secret.encode(), to_email.encode(), hashlib.sha256).hexdigest()[:16]
                token = f"{email_b64}.{sig}"
                unsub_url = f"{unsub_base}/unsubscribe?token={token}"
                msg["List-Unsubscribe"] = f"<{unsub_url}>"
                msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

            plain = "Jūsu e-pasta klients neatbalsta HTML. Lai atrakstītos, apmeklējiet saiti e-pasta beigās."
            msg.attach(MIMEText(plain, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            server.sendmail(gmail_address, to_email, msg.as_string())
            print(f"  ✓ {to_email}")
            time.sleep(0.5)
            return True
    except Exception as e:
        print(f"  ✗ {to_email}: {e}")
        return False
