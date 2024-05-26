from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from ..models import User
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rute for innlogging av brukere.

    Hvis forespørselen er POST, validerer brukernavn og passord. Hvis de er gyldige blir brukeren logget inn.
    Hvis forespørselen er GET, vises innloggingssiden.
    """
    if request.method == 'POST':
        # Henter brukernavn og passord fra innloggingsskjemaet
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()

        if user and check_password_hash(user.Password, password):
            # Logger inn brukeren hvis brukernavn og passord er gyldige
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth.home'))
        else:
            flash('Ugyldig brukernavn eller passord!', 'danger')

    # Viser innloggingssiden hvis forespørselen er GET eller innlogging mislykkes
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    Rute for utlogging av brukere.

    Logger ut brukeren og viser en bekreftelsesmelding.
    """
    logout_user()
    flash('Du er logget ut!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """
    Rute for hjemsiden.

    Krever at brukeren er logget inn. Viser hjemsiden med brukerinformasjon.

    Returns:
        Response: Render hjemsiden med brukerinformasjon.
    """
    return render_template('main/home.html', user=current_user)
