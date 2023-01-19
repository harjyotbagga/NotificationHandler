import os
import sendgrid
from jinja2 import Environment, FileSystemLoader
from sendgrid.helpers.mail import *
from .exporter import SENDGRID_API_KEY
from . import exceptions


def render_email_template(template_name, email_body):
        TEMPLATES_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR_PATH))
        template = env.get_template(template_name)
        return template.render(email_body)


def write_debug_output(output):
    TEMPLATES_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    with open(os.path.join(TEMPLATES_DIR_PATH, 'output.html'), 'w') as fh:
        fh.write(output)
        

def send_email(source_email, email_recepients, email_subject, email_body):
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        from_email = Email(source_email)
        to_email = []
        for recepient in email_recepients:
            to_email.append(To(recepient))
        subject = email_subject
        mail = Mail(from_email=from_email, to_emails=to_email, subject=subject, html_content=email_body, is_multiple=True)
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code >= 400:
            raise exceptions.EmailNotSentException()