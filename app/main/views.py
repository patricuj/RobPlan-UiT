from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import main

@main.route('/')
def index():
    return render_template('/auth/login.html')

@main.route('/home')
@login_required
def home():
    return render_template('/main/home.html', user=current_user)
