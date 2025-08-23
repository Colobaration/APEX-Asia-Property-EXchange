from typing import Optional
import smtplib
from email.mime.text import MIMEText
from app.core.config import settings


class EmailClient:
    """Simple SMTP client for plain-text messages."""

    def __init__(self, server: Optional[str] = None, port: Optional[int] = None,
                 user: Optional[str] = None, password: Optional[str] = None) -> None:
        self.server = server or settings.smtp_server
        self.port = port or settings.smtp_port or 587
        self.user = user or settings.smtp_user
        self.password = password or settings.smtp_password

    def send(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None) -> None:
        if not (self.server and self.user and self.password):
            raise RuntimeError("SMTP is not configured. Set SMTP_SERVER/SMTP_PORT/SMTP_USER/SMTP_PASSWORD")
        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email or self.user
        msg["To"] = to_email

        with smtplib.SMTP(self.server, int(self.port)) as smtp:
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.sendmail(msg["From"], [to_email], msg.as_string())


