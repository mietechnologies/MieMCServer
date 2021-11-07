import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

class PiMailer:
    server = ''
    port = 0
    username = ''
    password = ''
    
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
    
    def sendMail(self, recipient, subject, content, attachments = []):
        message = MIMEMultipart()
        message['From'] = self.username
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(content))
        
        # attach files
        for attachment in attachments:
            with open (attachment, "rb") as file:
                part = MIMEApplication(file.read(), Name=basename(attachment))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
            message.attach(part)
        
        # connect to server
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo()
        
        # login
        session.login(self.username, self.password)
        
        # send email and exit
        session.sendmail(self.username, recipient, message.as_string())
        session.quit()
        