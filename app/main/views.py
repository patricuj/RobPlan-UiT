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

@main.route('/robot_status/<isar_id>')
@login_required
def robot_status(isar_id):
    return render_template('/robot_status/robot_status.html', isar_id=isar_id)
