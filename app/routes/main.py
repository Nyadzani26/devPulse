from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import User, Pulse, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        content = request.form.get('content')
        parent_id = request.form.get('parent_id')
        
        if not parent_id or parent_id == "":
            parent_id = None
            
        new_pulse = Pulse(content=content, user_id=user.id, parent_id=parent_id)
        db.session.add(new_pulse)
        db.session.commit()

        flash('Milestone updated' if parent_id else 'New Milestone created!')
        return redirect(url_for('main.dashboard'))

    all_pulses = Pulse.query.filter_by(parent_id=None).order_by(Pulse.id.desc()).all()
    return render_template('dashboard.html', user=user, pulses=all_pulses)

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.bio = request.form.get('bio')
        user.primary_stack = request.form.get('primary_stack')
        user.github_username = request.form.get('github_username')
        user.website_url = request.form.get('website_url')

        db.session.commit()

        flash('Profile updated successfully')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_profile.html', user=user)

@main.route('/follow/<int:user_id>')
def follow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_to_follow = User.query.get(user_id)
    current_user = User.query.get(session['user_id'])

    if user_to_follow is None:
        flash("User not found")
        return redirect(url_for('main.dashboard'))

    if user_to_follow.id == current_user.id:
        flash('You cannot follow yourself')
        return redirect(url_for('main.dashboard'))

    if user_to_follow not in current_user.followed:
        current_user.followed.append(user_to_follow)
        db.session.commit()
        flash(f'You are now following {user_to_follow.first_name} {user_to_follow.last_name}!')
    else:
        flash('You are already following this user')

    return redirect(url_for('main.dashboard'))

@main.route('/unfollow/<int:user_id>') 
def unfollow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_to_unfollow = User.query.get(user_id)
    current_user = User.query.get(session['user_id'])

    if user_to_unfollow and user_to_unfollow in current_user.followed:
        current_user.followed.remove(user_to_unfollow)
        db.session.commit()
        flash(f'You stopped following {user_to_unfollow.first_name} {user_to_unfollow.last_name}.')
        
    return redirect(url_for('main.dashboard'))
