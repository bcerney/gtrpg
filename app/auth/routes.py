from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import (LoginForm, RegistrationForm, ResetPasswordForm,
                            ResetPasswordRequestForm)
from app.models import User, UserSchema


USER_SCHEMA = UserSchema(exclude=("last_seen", ))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first_or_404()
        get_dumped_user(user)

        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)
    return render_template('auth/login.html', title='Log In | gtRPG', form=login_form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    level=1,
                    xp=0,
                    xp_to_next_level=5,
                    level_up_xp_modifier=5)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register | gtRPG', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(f'An email has been sent to {user.username} with instructions to reset your password.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Request Password Reset | gtRPG', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password | gtRPG', form=form)


# Utility functions
# TODO: move to proper class

def get_dumped_user(user):
    dumped_user = USER_SCHEMA.dump(user)
    # flash(f'dumped_user={dumped_user}')
    return dumped_user
