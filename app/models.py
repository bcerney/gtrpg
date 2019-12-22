from datetime import datetime
from time import time

import jwt
from flask import current_app as app
from flask import flash
from flask_login import UserMixin
from marshmallow import fields, post_load
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login, ma


class UserCategory(db.Model):
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
    level = db.Column('user_category_level', db.Integer, default=1, index=True)
    xp = db.Column('user_category_xp', db.Integer, default=0, index=True)
    level_up_xp_modifier = db.Column(db.Integer, default=5)
    xp_to_next_level = db.Column(db.Integer, default=5)
    xp_to_next_level_constant = db.Column(db.Float, default=5.0)

    def __repr__(self):
        return f'<UserCategory: user_id={self.user_id}, \
                  category_id={self.category_id}, \
                  level={self.level}, \
                  xp={self.xp}, \
                  level_up_xp_modifier={self.level_up_xp_modifier}, \
                  xp_to_next_level={self.xp_to_next_level}, \
                  xp_to_next_level_constant={self.xp_to_next_level_constant}>'


class User(UserMixin, db.Model):
    # TODO: add timestamp, probably as Mixin?
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    level = db.Column(db.Integer, default=1, index=True)
    xp = db.Column(db.Integer, default=0, index=True)
    level_up_xp_modifier = db.Column(db.Integer, default=5, index=True)
    xp_to_next_level = db.Column(db.Integer, default=5, index=True)
    xp_to_next_level_constant = db.Column(db.Float, default=5.0)

    user_category = db.relationship('UserCategory', lazy=True)

    def __repr__(self):
        return f'<User: id={self.id}, \
                    username={self.username}, \
                    email={self.email}, \
                    about_me={self.about_me}, \
                    last_seen={self.last_seen}, \
                    level={self.level}, \
                    xp={self.xp}, \
                    xp_to_next_level={self.xp_to_next_level}, \
                    xp_to_next_level_constant={self.xp_to_next_level_constant}, \
                    level_up_xp_modifier={self.level_up_xp_modifier}, \
                    user_category={self.user_category}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            flash(f'Exception occured: {e}')
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserSchema(ma.ModelSchema):
    last_seen = fields.DateTime()

    class Meta:
        model = User


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category: id={self.id}, \
                  title={self.title}>, \
                  description={self.description}, \
                  tasks={self.tasks}>'


session_tasks_atable = db.Table('session_tasks_atable',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id')),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    completed = db.Column(db.DateTime, index=True)
    tasks = db.relationship('Task', secondary=session_tasks_atable)
    is_draft = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Session: id={self.id}, \
                  user_id={self.user_id}>, \
                  created={self.created}>, \
                  completed={self.completed}>, \
                  is_draft={self.is_draft}, \
                  tasks={self.tasks}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    xp = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<Task: id={self.id}, \
                user_id={self.user_id,}>, \
                category_id={self.category_id}, \
                timestamp={self.timestamp} \
                title={self.title,}>, \
                description={self.description}, \
                xp={self.xp}'


class TaskSchema(ma.ModelSchema):
    timestamp = fields.DateTime()

    @post_load
    def make_task(self, data, **kwargs):
        return Task(**data)

    class Meta:
        model = Task
