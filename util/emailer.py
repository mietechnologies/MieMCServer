from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .configuration import Email
from os.path import basename, normpath
import smtplib
import base64


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
            with open(attachment, 'rb') as file:
                attachment_file = MIMEApplication(file.read(), _subtype="txt")
                name = basename(normpath(attachment))
                attachment_file.add_header("Content-Disposition",
                                           "attachment",
                                           filename=name)
                msg.attach(attachment_file)

        server = smtplib.SMTP(Email.server, Email.port)
        server.starttls()
        server.login(Email.address, Email.password)
        server.sendmail(Email.address, Email.recipients, msg.as_string())

        server.quit()
