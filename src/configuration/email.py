import base64
from util.mielib import custominput as ci

class Email:
    data = {}
    address = '<your.email@gmail.com>'
    password = '<your password>'
    server = 'smtp.gmail.com'
    port = 587
    recipients = []

    def __init__(self, data: dict):
        self.data = data
        self.address = self.data.get('address', '<your.email@gmail.com>')
        self.server = self.data.get('server', 'smtp.gmail.com')
        self.port = self.data.get('port', 587)
        self.recipients = self.data.get('recipients', [])

        try:
            password = self.data.get('password', '')
            password = base64.b64decode(password)
            self.password = password.decode('utf-8')
        except UnicodeDecodeError:
            self.password = '<your password>'

    def build(self) -> dict:
        email_address = ci.email_input("What is the gmail address you would " \
            "like me to use to send you reports?", provider="gmail")
        password = ci.password_input("What is the password to the account you" \
            " just entered?")
        recipients = ci.email_input("What email address(es) would you like " \
            "to recieve the logs and reports?", multiples=True)
        self.address = email_address
        self.password = password
        self.recipients = recipients
        return self.update()

    def update(self) -> dict:
        self.data["address"] = self.address
        self.data["password"] = base64.b64encode(self.password.encode('utf-8'))
        self.data["server"] = self.server
        self.data["port"] = self.port
        self.data["recipients"] = self.recipients
        return self.data

    def reset(self):
        self.address = "<your.email@gmail.com>"
        self.password = "<your password>"
        self.server = "smtp.gmail.com"
        self.port = 587
        self.recipients = []
