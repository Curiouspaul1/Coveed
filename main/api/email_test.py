import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import jsonify,render_template,current_app
from urllib.error import URLError

"""def EmergencyMail(mail_subject):
    This function utilizes SendGrid Api to send emergcency signals as email
    to the necessary agencies
    message = Mail(
        from_email = current_app.config['APP_EMAIL'],
        to_emails = current_app.config['AGENT_EMAIL'],
        subject = mail_subject,
        html_content = render_template('Emergency.html')
    )

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    print(sg)
    try:
        resp = sg.send(message)
        return True
    except URLError as e:
        #print(f"{resp.status_code}'\n'{resp.body}'\n'{resp.headers}")
        raise e
        return False
    else:
        raise e
        return False
"""

message = Mail(
    from_email = 'paulcurious7@gmail.com',#current_app.config['APP_EMAIL'],
    to_emails = 'asalupaul36@gmail.com',#current_app.config['AGENT_EMAIL'],
    subject = 'Emergency',
    html_content = 'Emergency.html'
)

sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
print(sg)
try:
    resp = sg.send(message)
    #return True
except URLError as e:
    #print(f"{resp.status_code}'\n'{resp.body}'\n'{resp.headers}")
    raise e
    #return False
else:
    raise e
    #return False