from flask import render_template
from . import robot_fleet_bp
from .. import socketio


@robot_fleet_bp.route('/robot_fleet')
def robot_fleet():
    return render_template('/robot_fleet/robot_fleet.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


    