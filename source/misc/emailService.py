# External
import smtplib
import ssl


class EmailService:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 465
        self.email = 'nisdiploma1488'
        self.password = 'qwerty_1488'
        self.context = ssl.create_default_context()

    def notify_add(self, username, password, receiver):
        self.send_message(f"Subject:New account created\n\nAn account has been created:\n"
                          f"Username: {username}\nPassword: {password}", receiver)

    def notify_edit(self, username, password, receiver):
        self.send_message(f"Subject:Your account updated\n\nYour account has been updated:\n"
                          f"Username: {username}\nPassword: {password}", receiver)

    def notify_delete(self, receiver):
        self.send_message(f"Subject:Your account deleted\n\nYour account has been deleted", receiver)

    def notify_restore(self, username, password, receiver):
        self.send_message(f"Subject:Password restoration\n\n"
                          f"Your password has been restored:\nUsername: {username}\n"
                          f"Password: {password}", receiver)

    def send_message(self, message, receiver):
        try:
            with smtplib.SMTP_SSL(self.host, self.port, context=self.context) as server:
                server.login(self.email, self.password)
                server.sendmail(self.email, receiver, message)
        except Exception as err:
            print(err)
