from flask import Blueprint, render_template, request, jsonify, json, redirect, flash, url_for
import requests
from . import missions_bp
from ..models import Mission
from ..extensions import db
import random
import time
@missions_bp.route('/missions')
def missions():
    all_missions = Mission.query.all()
    print("Sending missions data:", all_missions)
    return render_template('missions/missions.html', missions=all_missions)


recent_ports = {}
recent_calls = []

def set_missions_availability(is_available):
    missions = Mission.query.all()
    for mission in missions:
        mission.IsAvailable = is_available
    db.session.commit()

@missions_bp.route('/start-mission', methods=['POST'])
def start_mission():
    global recent_ports, recent_calls

    current_time = time.time()
    recent_calls.append(current_time)

    recent_calls = [call for call in recent_calls if current_time - call <= 3]

    if len(recent_calls) >= 1:
        set_missions_availability(False)

    
    ports = [3000, 4000]
    valid_ports = [port for port in ports if port not in recent_ports or (current_time - recent_ports[port] > 10)]

    if not valid_ports:
        return jsonify({"error": "No valid ports available. Please try again later."}), 503

    port = random.choice(valid_ports)
    recent_ports[port] = current_time

    isar_api_url = f'http://localhost:{port}/schedule/start-mission'
    default_mission_data = request.json

    transformed_data = transform_mission_data(default_mission_data)

    response = requests.post(isar_api_url, json=transformed_data)
    
    if response.status_code == 200:
        return jsonify({"message": "Mission successfully started", "data": response.json()}), 200
    else:
        return jsonify({"error": "Failed to start mission", "details": response.text}), response.status_code


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




@missions_bp.route('/schedule/stop-mission', methods=['POST'])
def stop_mission():
    isar_api_url = 'http://localhost:3000/schedule/stop-mission'
    response = requests.post(isar_api_url)

    if response.status_code == 200:
        return jsonify({"message": "Oppdrag stoppet"}), 200
    else:
        return jsonify({"error": "Kunne ikke stoppe oppdraget", "details": response.text}), response.status_code

@missions_bp.route('/schedule/pause-mission', methods=['POST'])
def pause_mission():
    isar_api_url = 'http://localhost:3000/schedule/pause-mission'
    response = requests.post(isar_api_url)
    
    if response.status_code == 200:
        return jsonify({"message": "Oppdrag er pauset"}), 200
    else:
        return jsonify({"error": "Kunne ikke pause oppdraget",
                        "details": response.text}), response.status_code


@missions_bp.route('/schedule/resume-mission', methods=['POST'])
def resume_mission():
    isar_api_url = 'http://localhost:3000/schedule/resume-mission'
    response = requests.post(isar_api_url)
    
    if response.status_code == 200:
        return jsonify({"message": "Oppdrag er gjenopptatt"}), 200
    else:
        return jsonify({"error": "Kunne ikke gjenoppta oppdraget", "details": response.text}), response.status_code


@missions_bp.route('/add-mission', methods=['POST'])
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
def delete_mission(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    db.session.delete(mission)
    db.session.commit()
    flash('Oppdrag slettet.', 'success')
    return redirect(url_for('missions.missions'))

@missions_bp.route('/edit-mission', methods=['POST'])
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
def make_all_missions_available():
    missions = Mission.query.all()
    for mission in missions:
        mission.IsAvailable = True
    db.session.commit()
    return jsonify({"message": "Alle oppdrag er nå tilgjengelige"}), 200