import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import sys


class SingletonMeta(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance


class EmailManager(metaclass=SingletonMeta):
    def __init__(self, host, port, user, password, charset="utf-8"):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._charset = charset

    def send_email(self, subject, content, receiver, msgRoot=None, mimeType="plain"):
        try:
            server = smtplib.SMTP_SSL(self._host, self._port)
            server.login(self._user, self._password)

            if msgRoot:
                contentApp = MIMEText(content, mimeType, _charset=self._charset)
                msgRoot.attach(contentApp)
                msg = msgRoot
            else:
                msg = MIMEText(content, mimeType, self._charset)

            msg["Subject"] = subject
            msg["From"] = self._user
            msg["To"] = ",".join(receiver)
            result = server.sendmail(self._user, receiver, msg.as_string())
            stderr = result if result else None
        except Exception as e:
            stderr = str(e)
        return stderr

    def send_file(self, subject, content, receiver, file):
        try:
            filename = os.path.basename(file)
            msgRoot = MIMEMultipart("relate")

            fileApp = MIMEApplication(open(file, "rb").read())
            fileApp.add_header("Content-Type", "application/octet-stream")
            fileApp.add_header("Content-Disposition", "attachment", filename=filename)
            msgRoot.attach(fileApp)

            stderr = self.send_email(subject, content, receiver, msgRoot)
        except Exception as e:
            stderr = str(e)
        return stderr


if __name__ == "__main__":
    smtpServer = "smtp.163.com"
    sender = "18719091650@163.com"
    passWd = "qq5201314ouru"
    receiver = ["gzgdouru@163.com"]

    email_obj = EmailManager(smtpServer, sender, passWd)
