from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Hashing Tools!
from config import config_options

app = Flask(__name__)
app.config.from_object(config_options['development'])
db = SQLAlchemy(app)

# The "Bridge Table" - stores who follows whom
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

# Our models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    
    # We never store "password", we store password_hash
    password_hash = db.Column(db.String(128))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken')
            return redirect(url_for('register'))

        # If not exist, we will hash the password for the new user
        hashed_pw = generate_password_hash(password)

        # Create the new user object
        new_user = User(username=username, password_hash=hashed_pw)

        # Save the user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id # Give the user a session ID
            flash('Login successful')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password! Please try again.')
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
        flash(f'You are now following @{user_to_follow.username}!')
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
        flash(f'You stopped following @{user_to_unfollow.username}.')
        
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # When app runs we create db tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    