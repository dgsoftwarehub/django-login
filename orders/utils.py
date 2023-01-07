import environ
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

env = environ.Env()
environ.Env.read_env()


def send_emails(sender, receiver, subject, html):
    """Send email for different purposes."""
    message = Mail(
        from_email=sender,
        to_emails=receiver,
        subject=subject,
        html_content=html
    )
    try:
        sg = SendGridAPIClient(env('EMAIL_PASS', default=''))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
