from flask import render_template, request, redirect, url_for
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')
