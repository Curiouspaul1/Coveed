import os,base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,Attachment,FileContent,FileName,
    FileType,Disposition,ContentId
)
from flask import jsonify,render_template,current_app
from urllib.error import URLError

def EmergencyMail(mail_subject,html_content,file_path):
    """This function utilizes SendGrid Api to send emergcency signals as email
    to the necessary agencies"""
    message = Mail(
        from_email = current_app.config['APP_EMAIL'],
        to_emails = current_app.config['AGENT_EMAIL'],
        subject = mail_subject,
        html_content = html_content
    )

    with open(file_path,'rb') as f:
        data = f.read()
        f.close()

    # encode file
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/xls')
    attachment.file_name = FileName('data.xls')
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('TestId')
    message.attachment = attachment
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        resp = sg.send(message)
        return True
    except URLError as e:
        #print(f"{resp.status_code}'\n'{resp.body}'\n'{resp.headers}")
        raise e
        return False
    else:
        raise e
        return False
