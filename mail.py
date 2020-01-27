# Read file, mail, and delete file
import os
import smtplib
from email.mime.text import MIMEText


# E-Mail
smtp_server = "smtp.hippke.org"
mail_from = "adsbot@hippke.org"
smtp_port = "587"
path = "mails/"


def send_mail_func(mailtext_content, adr):
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.login(mail_from, os.environ.get("SECRET_MAIL_PASSWORD"))
    msg = MIMEText("".join(mailtext_content))
    msg["Subject"] = "ADS bot: New citations"
    msg["From"] = mail_from
    msg["To"] = adr
    server.sendmail(mail_from, adr, msg.as_string())


if os.path.exists(path):
    print('Path exists:', path)
    for file in os.listdir(path):
        filehandle = open(path+file, "r")
        mailtext_content = filehandle.readlines()
        print('Mailing', path+file, mailtext_content)
        adr = file  # Mail address is filename
        send_mail_func(mailtext_content, adr)
        filehandle.close()
        os.remove(path+file)
