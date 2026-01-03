import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Hashing Tools!
from config import config_options
from datetime import datetime

app = Flask(__name__)

# We will use the config options to set the config
config_mode = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_options[config_mode])

db = SQLAlchemy(app)

# The "Bridge Table" - stores who follows whom
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

# Our models
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
    # backref='author' which means that each pulse will have a .author property
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
    content = db.Column(db.Text, nullable=False) # Like a tweet
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Validation
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        new_user = User(
            email=email, 
            password_hash=hashed_pw,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Tell us more about yourself in your profile.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id # Give the user a session ID
            flash(f'Welcome back, {user.first_name}!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password! Please try again.')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # We will only let login users acess this
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        content = request.form.get('content')
        new_pulse = Pulse(content=content, user_id=user.id)
        db.session.add(new_pulse)
        db.session.commit()

        flash('Pulse created successfully!')
        # Optional: redirect to self to clear the POST data
        return redirect(url_for('dashboard'))

    # Relational Power: we get all pulses from all users for the feed
    all_pulses = Pulse.query.order_by(Pulse.id.desc()).all()
    return render_template('dashboard.html', user=user, pulses=all_pulses)

@app.route('/logout')
def logout():
    # The session "pop" removes the wristband!
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        # Capturing form data
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.bio = request.form.get('bio')
        user.primary_stack = request.form.get('primary_stack')
        user.github_username = request.form.get('github_username')
        user.website_url = request.form.get('website_url')

        db.session.commit()

        flash('Profile updated successfully')
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html', user=user)

@app.route('/follow/<int:user_id>')
def follow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_to_follow = User.query.get(user_id)
    current_user = User.query.get(session['user_id'])

    if user_to_follow is None:
        flash("User not found")
        return redirect(url_for('dashboard'))

    if user_to_follow.id == current_user.id:
        flash('You cannot follow yourself')
        return redirect(url_for('dashboard'))

    if user_to_follow not in current_user.followed:
        current_user.followed.append(user_to_follow)
        db.session.commit()
        flash(f'You are now following {user_to_follow.first_name} {user_to_follow.last_name}!')
    else:
        flash('You are already following this user')

    return redirect(url_for('dashboard'))

@app.route('/unfollow/<int:user_id>') 
def unfollow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_to_unfollow = User.query.get(user_id)
    current_user = User.query.get(session['user_id'])

    if user_to_unfollow and user_to_unfollow in current_user.followed:
        current_user.followed.remove(user_to_unfollow)
        db.session.commit()
        flash(f'You stopped following {user_to_unfollow.first_name} {user_to_unfollow.last_name}.')
        
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # When app runs we create db tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    