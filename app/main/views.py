from flask import render_template
from flask_login import login_required, current_user
from . import main
from ..models import Mission

@main.route('/')
def index():
    """
    Rute for å vise innloggingssiden.
    """
    return render_template('/auth/login.html')

@main.route('/home')
@login_required
def home():
    """
    Rute for å vise hjemmesiden for innloggede brukere.
    """
    missions = Mission.query.all()
    return render_template('/main/home.html', user=current_user, missions=missions)
