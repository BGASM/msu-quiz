from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app


def send_mail(to, subject, body):
    message = Mail(
        from_email='accounts@qbank2024.me',
        to_emails=to,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        print(current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.body)