from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .configuration import Email
from os.path import basename
import smtplib


class Emailer:

    attachments = []

    def __init__(self, subject, body):
        self.subject = subject
        self.body = body

    def attach(self, file):
        self.attachments.append(file)

    def send(self):
        msg = MIMEMultipart()
        msg["From"] = Email.address
        msg["To"] = ", ".join(Email.recipients)
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.body, "plain"))

        for attachment in self.attachments:
            with open(attachment, "rb") as file:
                aFile = MIMEApplication(file.read(), _subtype="txt")
                aFile.add_header("Content-Disposition", "attachment",
                    filename=basename(file))
                msg.attach(file)

        server = smtplib.SMTP(Email.server, Email.port)
        server.starttls()
        server.login(Email.address, Email.password)
        server.sendmail(Email.address, self.recipients, msg.as_string())

        server.quit()
