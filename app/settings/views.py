from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .. import db
from ..models import User
from . import settings_bp

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Viser innstillinger-siden og håndterer oppdateringer av brukerkontoens e-postadresse.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        delete_email = request.form.get('delete_email')

        user = User.query.get(current_user.idUser)
        
        if delete_email:
            user.Email = None
            flash('E-postadressen din er fjernet.', 'success')
        elif email:
            user.Email = email
            flash('E-postadressen din er oppdatert.', 'success')
        else:
            flash('Vennligst oppgi en gyldig e-postadresse.', 'error')

        db.session.commit()
        return redirect(url_for('settings.settings'))

    return render_template('settings/settings.html')
