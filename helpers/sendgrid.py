import os
import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition)

from helpers import authentication


def send_mail(message):

    try:
        token = authentication.get_token('https://www.apitutor.org/sendgrid/key')
        sg = SendGridAPIClient(token)
        sg.send(message)
        return True

    except Exception as e:
        print(e)
        return False


def build_message(from_email: str, to_emails: tuple, subject: str,
                  html_content: str, file_name: str):

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content
    )

    if os.path.isfile(file_name):

        with open(file=file_name, mode='rb') as f:
            data = f.read()
            f.close()

        encoded = base64.b64encode(data).decode()

        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('application/html')
        attachment.file_name = FileName('Music_Recommendations.html')
        attachment.disposition = Disposition('attachment')

        message.attachment = attachment

    return message


def email(html_content: str, file_name: str):

    ans = input('Would you like to email this list to yourself?[y/n] ')

    if ans.lower() == 'yes' or ans.lower() == 'y':

        sender = input('Enter your email: ')
        receiver = input('Enter recipient email(s): ')
        receiver = tuple([n.strip() for n in receiver.split(',')])

        if len(receiver) <= 1:
            receiver = (receiver[0], sender)

        message = build_message(
            from_email=sender,
            to_emails=receiver,
            subject='New Music Recommendations',
            html_content=html_content,
            file_name=file_name
        )

        result = send_mail(message=message)

        if result:
            print('Email sent successfully!\n')
        else:
            print('Email sent unsuccessfully.\n')
