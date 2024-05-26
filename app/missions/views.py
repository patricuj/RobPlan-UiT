from flask import Blueprint, render_template, request, jsonify, json, redirect, flash, url_for
import requests
from . import missions_bp
from ..models import Mission, RobotInfo
from ..extensions import db
import random
from flask_login import login_required

@missions_bp.route('/missions')
@login_required
def missions():
    update_mission_availability_based_on_battery()
    
    all_missions = Mission.query.all()
    print("Sending missions data:", all_missions)
    return render_template('missions/missions.html', missions=all_missions)


def set_missions_availability(is_available):
    missions = Mission.query.all()
    for mission in missions:
        mission.IsAvailable = is_available
    db.session.commit()

def update_mission_availability_based_on_battery():
    subquery = db.session.query(
        RobotInfo.isar_id,
        db.func.max(RobotInfo.id).label('max_id')
    ).group_by(RobotInfo.isar_id).subquery()

    latest_robot_info = db.session.query(
        RobotInfo.isar_id, RobotInfo.battery_level, RobotInfo.robot_status
    ).join(subquery, RobotInfo.id == subquery.c.max_id).all()


    is_available = any(
        robot_info.battery_level is not None and 
        robot_info.battery_level > 60 and 
        robot_info.robot_status != 'busy' 
        for robot_info in latest_robot_info
    )
    if is_available:
        make_all_missions_available()
    else:
        make_all_missions_unavailable()



@missions_bp.route('/update-mission-availability', methods=['POST'])
@login_required
def update_mission_availability():
    update_mission_availability_based_on_battery()
    return jsonify({"message": "Mission availability updated based on robot battery levels"}), 200

@missions_bp.route('/start-mission', methods=['POST'])
@login_required
def start_mission():
    default_mission_data = request.json

    subquery = db.session.query(
        RobotInfo.isar_id,
        db.func.max(RobotInfo.id).label('max_id')
    ).group_by(RobotInfo.isar_id).subquery()

    latest_robot_info = db.session.query(
        RobotInfo.isar_id, RobotInfo.robot_name, RobotInfo.battery_level, RobotInfo.robot_status, RobotInfo.port
    ).join(subquery, RobotInfo.id == subquery.c.max_id).all()

    available_robot = next((robot for robot in latest_robot_info if robot.battery_level > 60 and robot.robot_status != 'busy'), None)

    if not available_robot or not available_robot.port:
        return jsonify({"error": "No available robot with sufficient battery, idle status, or valid port"}), 400

    isar_api_url = f'http://localhost:{available_robot.port}/schedule/start-mission'
    
    transformed_data = transform_mission_data(default_mission_data)

    try:
        response = requests.post(isar_api_url, json=transformed_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to start mission", "details": str(e)}), 500
    
    return jsonify({"message": "Mission successfully started", "data": response.json()}), 200


def transform_mission_data(default_mission_data):
    mission_id = default_mission_data.get('mission_definition', {}).get('id', 'default_id')
    mission_name = default_mission_data.get('mission_definition', {}).get('name', 'default_name')
    transformed_tasks = []
    for task in default_mission_data['tasks']:
        for step in task['steps']:
            if step['type'] == 'drive_to_pose':
                pose = {
                    "position": step['pose']['position'],
                    "orientation": step['pose']['orientation'],
                    "frame_name": step['pose'].get('frame', 'default_frame')
                }
            elif step['type'] in ['take_image', 'take_thermal_image']:
                transformed_task = {
                    "type": "inspection",
                    "pose": pose,
                    "inspections": [{
                        "type": "Image" if step['type'] == 'take_image' else "Thermal",
                        "inspection_target": step['target'],
                        "analysis_type": "string",
                        "duration": 0,
                        "metadata": {},
                        "id": "string"
                    }]
                }
                transformed_tasks.append(transformed_task)

    return {
        "mission_definition": {
            "id": mission_id,
            "name": mission_name,
            "tasks": transformed_tasks
        },
        "initial_pose": {
            "position": {"x": 0, "y": 0, "z": 0, "frame_name": "robot"},
            "orientation": {"x": 0, "y": 0, "z": 0, "w": 0, "frame_name": "robot"},
            "frame_name": "robot"
        },
        "return_pose": {
            "position": {"x": 0, "y": 0, "z": 0, "frame_name": "robot"},
            "orientation": {"x": 0, "y": 0, "z": 0, "w": 0, "frame_name": "robot"},
            "frame_name": "robot"
        }
    }


@missions_bp.route('/add-mission', methods=['POST'])
@login_required
def add_mission():
    mission_name = request.form.get('MissionName')
    mission_data = {
        "id": mission_name,
        "tasks": [{
            "steps": [
                {
                    "type": "drive_to_pose",
                    "pose": {
                        "position": {"x": -2, "y": -2, "z": 0, "frame": "asset"},
                        "orientation": {"x": 0, "y": 0, "z": 0.4794255, "w": 0.8775826, "frame": "asset"},
                        "frame": "asset"
                    }
                },
                {
                    "type": "take_image",
                    "target": {"x": 2, "y": 2, "z": 0, "frame": "robot"}
                }
            ]
        }]
    }
    port = random.choice([3000, 4000])
    status = request.form.get('Status', 'Ingen planlagt inspeksjon')
    
    deadline_date = request.form.get('DeadlineDate')
    deadline_time = request.form.get('DeadlineTime')
    
    if deadline_date:
        if deadline_time:
            deadline = f"{deadline_date} {deadline_time}:00"
        else:
            deadline = f"{deadline_date} 00:00:00"
    else:
        deadline = None

    new_mission = Mission(
        MissionName=mission_name,
        MissionData=json.dumps(mission_data),
        IsAvailable=True,
        Port=port,
        Status=status,
        LastCompleted=None,
        Deadline=deadline
    )
    db.session.add(new_mission)
    db.session.commit()
    flash('Nytt oppdrag lagt til!', 'success')
    return redirect(url_for('missions.missions'))

@missions_bp.route('/delete-mission/<int:mission_id>', methods=['POST'])
@login_required
def delete_mission(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    db.session.delete(mission)
    db.session.commit()
    flash('Oppdrag slettet.', 'success')
    return redirect(url_for('missions.missions'))

@missions_bp.route('/edit-mission', methods=['POST'])
@login_required
def edit_mission():
    mission_id = request.form.get('MissionId')
    mission_name = request.form.get('MissionName')
    status = request.form.get('Status')
    deadline_date = request.form.get('DeadlineDate')
    deadline_time = request.form.get('DeadlineTime')
    
    if deadline_date:
        if deadline_time:
            deadline = f"{deadline_date} {deadline_time}:00"
        else:
            deadline = f"{deadline_date} 00:00:00"
    else:
        deadline = None

    mission = Mission.query.get(mission_id)
    if mission:
        mission.MissionName = mission_name
        mission.Status = status
        mission.Deadline = deadline
        db.session.commit()
        flash('Oppdrag oppdatert!', 'success')
    else:
        flash('Oppdrag ikke funnet.', 'danger')

    return redirect(url_for('missions.missions'))

@missions_bp.route('/make-all-missions-available', methods=['POST'])
@login_required
def make_all_missions_available():
    set_missions_availability(True)
    return jsonify({"message": "Alle oppdrag er nå tilgjengelige"}), 200

@missions_bp.route('/make-all-missions-unavailable', methods=['POST'])
@login_required
def make_all_missions_unavailable():
    set_missions_availability(False)
    return jsonify({"message": "Alle oppdrag er nå utilgjengelige"}), 200
