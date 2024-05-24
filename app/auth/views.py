from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from ..models import User
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()

        if user and check_password_hash(user.Password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth.home'))
        else:
            flash('Ugyldig brukernavn eller passord!', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Du er logget ut!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('main/home.html', user=current_user)
