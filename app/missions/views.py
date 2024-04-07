from flask import render_template, request, jsonify
import requests
from . import missions_bp

@missions_bp.route('/missions')
def missions():
    return render_template('/missions/missions.html')

@missions_bp.route('/start-mission', methods=['POST'])
def start_mission():
    isar_api_url = 'http://localhost:3000/schedule/start-mission'
    default_mission_data = request.json

    transformed_data = transform_mission_data(default_mission_data)

    response = requests.post(isar_api_url, json=transformed_data)
    
    if response.status_code == 200:
        return jsonify({"message": "Mission successfully started", "data": response.json()}), 200
    else:
        return jsonify({"error": "Failed to start mission", "details": response.text}), response.status_code

def transform_mission_data(default_mission_data):
    transformed_tasks = []
    for task in default_mission_data['tasks']:
        transformed_task = {
            "type": "inspection",
            "pose": {},
            "inspections": []
        }
        for step in task['steps']:
            if step['type'] == 'drive_to_pose':
                transformed_task['pose'] = {
                    "position": step['pose']['position'],
                    "orientation": step['pose']['orientation'],
                    "frame_name": step['pose']['frame']
                }
            elif step['type'] == 'take_image' or step['type'] == 'take_thermal_image':
                transformed_task['inspections'].append({
                    "type": "Image" if step['type'] == 'take_image' else "Thermal",
                    "inspection_target": step['target'],
                    "analysis_type": "string",
                    "duration": 0,
                    "metadata": {},
                    "id": "string"
                })
        transformed_tasks.append(transformed_task)
    
    return {
        "mission_definition": {
            "id": "string",
            "name": "string",
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
        return jsonify({"message": "Oppdrag vellykket stoppet"}), 200
    else:
        return jsonify({"error": "Kunne ikke stoppe oppdraget", "details": response.text}), response.status_code

@missions_bp.route('/schedule/pause-mission', methods=['POST'])
def pause_mission():
    isar_api_url = 'http://localhost:3000/schedule/pause-mission'
    response = requests.post(isar_api_url)
    
    if response.status_code == 200:
        return jsonify({"message": "Oppdrag er pauset"})
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
