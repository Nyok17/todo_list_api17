from extensions import db
from datetime import datetime, timezone


class User(db.Model):
    """A class to describe User model with its attributes"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    todos = db.relationship('Todo', backref='user')
    

class Todo(db.Model):
    """A class to decribe Task model with its attributes"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.Date, default=datetime.now(timezone.utc))