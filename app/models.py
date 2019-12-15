from datetime import datetime
from time import time

import jwt
from flask_login import UserMixin
from marshmallow import fields
from werkzeug.security import check_password_hash, generate_password_hash

import app
from app import db, login, ma

# followers = db.Table('followers',
#     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
# )


class UserCategory(db.Model):
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
    level = db.Column('user_category_level', db.Integer)
    xp = db.Column('user_category_xp', db.Integer)

    def __repr__(self):
        return f'<UserCategory: user_id={self.user_id}, category_id={self.category_id}, level={self.level}, xp={self.xp}>'


class User(UserMixin, db.Model):
    # TODO: add timestamp, probably as Mixin?
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    level = db.Column(db.Integer, index=True)
    total_xp = db.Column(db.Integer, index=True)
    xp_to_next_level = db.Column(db.Integer, index=True)
    level_up_xp_modifier = db.Column(db.Integer, index=True)

    user_category = db.relationship('UserCategory', lazy=True)
    
    def __repr__(self):
        return f'<User: id={self.id}, \
                    username={self.username}, \
                    email={self.email}, \
                    about_me={self.about_me}, \
                    last_seen={self.last_seen}, \
                    level={self.level}, \
                    level={self.level}, \
                    total_xp={self.total_xp}, \
                    xp_to_next_level={self.xp_to_next_level}, \
                    level_up_xp_modifier={self.level_up_xp_modifier}, \
                    user_category={self.user_category}>'

    # followed = db.relationship(
    #     'User', secondary=followers,
    #     primaryjoin=(followers.c.follower_id == id),
    #     secondaryjoin=(followers.c.followed_id == id),
    #     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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
        except:
            return
        return User.query.get(id)

    # def follow(self, user):
    #     if not self.is_following(user):
    #         self.followed.append(user)

    # def unfollow(self, user):
    #     if self.is_following(user):
    #         self.followed.remove(user)

    # def is_following(self, user):
    #     return self.followed.filter(
    #         followers.c.followed_id == user.id).count() > 0

# TODO: add logging to help determine how loader is used
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
        return f'<Category: id={self.id}, title={self.title}>, description={self.description}, tasks={self.tasks}'

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
