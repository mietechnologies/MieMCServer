from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename, normpath
import smtplib


class Mailer:
    '''A simple object to send text emails with or without attachment files.'''

    __configuration = None

    attachments = []

    def __init__(self, subject, body, configuration):
        self.subject = subject
        self.body = body
        self.__configuration = configuration

    def attach(self, file):
        '''Attaches a file to the email. This can be called multiple times to
        attach multiple files. file is representative of a file path'''
        self.attachments.append(file)

    def send(self):
        '''Compiles the optional attachments and creates an email then uses
        the user's configuration to send the email along with its attachments'''
        msg = MIMEMultipart()
        msg["From"] = self.__configuration.email.address
        msg["To"] = ", ".join(self.__configuration.email.recipients)
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

        email_config = self.__configuration.email
        server = smtplib.SMTP(email_config.server, email_config.port)
        server.starttls()
        server.login(email_config.address, email_config.password)
        server.sendmail(email_config.address, email_config.recipients, msg.as_string())

        server.quit()
