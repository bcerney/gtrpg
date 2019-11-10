from app import db
from datetime import datetime

class User(db.Model):
    # TODO: add timestamp, probably as Mixin?
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    total_points = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<User: id={self.id}, username={self.username}, email={self.email}, total_points={self.total_points}>'

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
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Task: id={self.id}, title={self.title,}>, description={self.description}, category_id={self.category_id}'