from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# The "Bridge Table" - stores who follows whom
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.String(500))
    primary_stack = db.Column(db.String(100))
    github_username = db.Column(db.String(100))
    website_url = db.Column(db.String(100))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: Link back to pulses
    pulses = db.relationship('Pulse', backref='author', lazy=True)

    # Relationship: Link back to followers
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Pulse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('pulse.id'))
    
    # Link to previous pulse/version
    updates = db.relationship('Pulse', backref=db.backref('parent', remote_side=[id]), lazy=True)
