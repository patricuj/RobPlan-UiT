from flask import render_template
from . import robot_fleet_bp


@robot_fleet_bp.route('/robot_fleet')
def robot_fleet():
    return render_template('robot_fleet.html')