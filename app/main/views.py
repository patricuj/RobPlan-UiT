from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import requests
from . import main

@main.route('/')
def index():
    return render_template('/main/home.html')

@main.route('/missions')
def missions():
    return render_template('/missions/missions.html')


@main.route('/robot_fleet')
def robot_fleet():
    return render_template('/robot_fleet/robot_fleet.html')
