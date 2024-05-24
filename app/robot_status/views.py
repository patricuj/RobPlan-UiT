from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import requests
from . import robot_status_bp
from ..models import RobotInfo
from sqlalchemy.sql import func
from ..extensions import db

@robot_status_bp.route('/robot_status/<isar_id>')
@login_required
def robot_status(isar_id):
    return render_template('/robot_status/robot_status.html', isar_id=isar_id)

@robot_status_bp.route('/api/robot_info/<isar_id>', methods=['GET'])
@login_required
def get_robot_info(isar_id):
    subquery = db.session.query(
        RobotInfo.isar_id,
        func.max(RobotInfo.id).label('latest_id')
    ).group_by(RobotInfo.isar_id).subquery()

    robot = db.session.query(RobotInfo).join(
        subquery, RobotInfo.id == subquery.c.latest_id
    ).filter(RobotInfo.isar_id == isar_id).first()

    if not robot:
        return jsonify({"error": "Robot not found"}), 404

    battery_level = robot.battery_level
    if battery_level is None:
        previous_battery = db.session.query(RobotInfo.battery_level).filter(
            RobotInfo.isar_id == robot.isar_id,
            RobotInfo.battery_level != None
        ).order_by(RobotInfo.id.desc()).first()
        battery_level = previous_battery[0] if previous_battery else 0

    robot_data = {
        'isar_id': robot.isar_id,
        'robot_name': robot.robot_name,
        'battery_level': battery_level,
        'robot_status': robot.robot_status,
        'current_mission_id': robot.current_mission_id,
        'port': robot.port
    }
    return jsonify(robot_data)

@robot_status_bp.route('/api/robot/<isar_id>/stop', methods=['POST'])
@login_required
def stop_robot(isar_id):
    robot = RobotInfo.query.filter_by(isar_id=isar_id).order_by(RobotInfo.id.desc()).first()
    if robot and robot.port:
        url = f'http://localhost:{robot.port}/schedule/stop-mission'
        try:
            response = requests.post(url)
            response.raise_for_status()
            return jsonify({"message": "Oppdrag stoppet vellykket"}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Kunne ikke stoppe oppdraget", "details": str(e)}), 500
    return jsonify({"error": "Robot not found or port not defined"}), 404

@robot_status_bp.route('/api/robot/<isar_id>/pause', methods=['POST'])
@login_required
def pause_robot(isar_id):
    robot = RobotInfo.query.filter_by(isar_id=isar_id).order_by(RobotInfo.id.desc()).first()
    if robot and robot.port:
        url = f'http://localhost:{robot.port}/schedule/pause-mission'
        try:
            response = requests.post(url)
            response.raise_for_status()
            return jsonify({"message": "Oppdrag satt på pause"}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Kunne ikke pause oppdraget", "details": str(e)}), 500
    return jsonify({"error": "Robot not found or port not defined"}), 404

@robot_status_bp.route('/api/robot/<isar_id>/resume', methods=['POST'])
@login_required
def resume_robot(isar_id):
    robot = RobotInfo.query.filter_by(isar_id=isar_id).order_by(RobotInfo.id.desc()).first()
    if robot and robot.port:
        url = f'http://localhost:{robot.port}/schedule/resume-mission'
        try:
            response = requests.post(url)
            response.raise_for_status()
            return jsonify({"message": "Oppdraget fortsetter"}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Kunne ikke fortsette oppdraget", "details": str(e)}), 500
    return jsonify({"error": "Robot not found or port not defined"}), 404
