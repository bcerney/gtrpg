from threading import Thread

from flask import current_app
from flask import flash
from flask_mail import Message
from werkzeug.local import LocalProxy


from app import mail


def send_async_email(app, msg):
    # if type(current_app) is LocalProxy:
    #     pass
    # if type(app) is LocalProxy:
    #     app_test = app._get_current_object()
    # flash('test')
    # flash(f'{msg}')
    # flash(f'{app}')
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    flash(f'{current_app._get_current_object()}')
    # https://stackoverflow.com/questions/40326651/flask-mail-sending-email-asynchronously-based-on-flask-cookiecutter
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    flash(f'app={app.app_context()},msg={msg}')
    Thread(target=send_async_email, args=(app, msg)).start()
