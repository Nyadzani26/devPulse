from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('auth.register'))

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
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.first_name}!')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password! Please try again.')
            return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('auth.login'))
