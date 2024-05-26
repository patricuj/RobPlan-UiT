from flask import render_template, jsonify
from . import robot_fleet_bp
from .. import socketio
from ..models import RobotInfo
from sqlalchemy.sql import func
from ..extensions import db
from flask_login import login_required

@robot_fleet_bp.route('/robot_fleet')
@login_required
def robot_fleet():
    robots = RobotInfo.query.all()
    return render_template('/robot_fleet/robot_fleet.html', robots=robots)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@robot_fleet_bp.route('/api/robot_info', methods=['GET'])
@login_required
def get_latest_robot_info():
    subquery = db.session.query(
        RobotInfo.isar_id,
        func.max(RobotInfo.id).label('latest_id')
    ).group_by(RobotInfo.isar_id).subquery()

    latest_records = db.session.query(RobotInfo).join(
        subquery, RobotInfo.id == subquery.c.latest_id
    ).all()

    robot_data = []
    for robot in latest_records:
        battery_level = robot.battery_level
        if battery_level is None:
            previous_battery = db.session.query(RobotInfo.battery_level).filter(
                RobotInfo.isar_id == robot.isar_id,
                RobotInfo.battery_level != None
            ).order_by(RobotInfo.id.desc()).first()
            battery_level = previous_battery[0] if previous_battery else 0

        robot_data.append({
            'isar_id': robot.isar_id,
            'robot_name': robot.robot_name,
            'battery_level': battery_level,
            'robot_status': robot.robot_status,
            'current_mission_id': robot.current_mission_id
        })
    return jsonify(robot_data)
    