# custom_email_backend.py
import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        if self.use_ssl:
            self.connection = smtplib.SMTP_SSL(
                self.host, self.port, timeout=self.timeout, context=ssl._create_unverified_context()
            )
        else:
            self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            if self.use_tls:
                self.connection.starttls(context=ssl._create_unverified_context())

        if self.username and self.password:
            self.connection.ehlo()
            if self.use_tls and not self.use_ssl:
                self.connection.starttls(context=ssl._create_unverified_context())
                self.connection.ehlo()
            self.connection.login(self.username, self.password)
        return True

    def close(self):
        if self.connection is None:
            return
        try:
            self.connection.quit()
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException):
            pass
        self.connection = None
