from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import requests
from . import missions_bp



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