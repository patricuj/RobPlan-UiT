from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import requests
from . import main

@main.route('/')
def index():
    return render_template('/main/home.html')


@main.route('/robot_status/<isar_id>')
def robot_status(isar_id):
    return render_template('/robot_status/robot_status.html', isar_id=isar_id)
