from flask import current_app as app
from flask import flash, render_template

from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[gtRPG] Reset Your Password',
                   sender=app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('email/reset_password.txt',
                                             user=user, token=token),
                   html_body=render_template('email/reset_password.html',
                                             user=user, token=token))
