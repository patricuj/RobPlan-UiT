import os
import json
from flask import render_template, abort
from . import report_bp
from datetime import datetime, timedelta
from ..models import Result
from flask_login import login_required, current_user

@report_bp.route('/report/<int:result_id>')
@login_required
def show_report(result_id):
    """
    Viser en rapport for et fullført oppdrag.

    """
    base_folder = os.getenv('RESULTS_DIR', '/default/path/to/results')
    target_json_suffix = f"__Image__{result_id}.json"
    found_json_path = None

    # Går i gjennom mappen for å finne JSON-filen med riktig result_id
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(target_json_suffix):
                found_json_path = os.path.join(root, file)
                break
        if found_json_path:
            break

    if not found_json_path:
        abort(404)

    try:
        # Leser JSON-filen og trekker ut nødvendige data
        with open(found_json_path, 'r') as file:
            data = json.load(file)
            timestamp_str = data["data"][0]["files"][0]["timestamp"]
            timestamp = datetime.fromisoformat(timestamp_str)

            start_time = timestamp - timedelta(hours=1)
            duration = '60 minutter'

            electric_box_time = start_time + timedelta(minutes=10)
            switch_audio_time = start_time + timedelta(minutes=20)
            valve_image_time = start_time + timedelta(minutes=45)

            report_data = {
                "mission_id": data["additional_meta"]["mission_id"],
                "mission_name": data["additional_meta"]["mission_name"],
                "plant_code": data["plant_code"],
                "plant_name": data["additional_meta"]["plant_name"],
                "isar_id": data["additional_meta"]["isar_id"],
                "robot_name": data["additional_meta"]["robot_name"],
                "analysis_type": data["additional_meta"]["analysis_type"],
                "timestamp": timestamp_str,
                "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": duration,
                "electric_box_time": electric_box_time.strftime('%Y-%m-%d %H:%M:%S'),
                "switch_audio_time": switch_audio_time.strftime('%Y-%m-%d %H:%M:%S'),
                "valve_image_time": valve_image_time.strftime('%Y-%m-%d %H:%M:%S'),
                "operator": current_user.Username
            }
            return render_template('report/report.html', report_data=report_data, result_id=result_id)
    except FileNotFoundError:
        abort(404)

@report_bp.route('/report/failed/<int:result_id>')
@login_required
def show_failed_report(result_id):
    """
    Viser en rapport for et mislykket oppdrag.
    """
    result = Result.query.get(result_id)
    if not result:
        abort(404)
    
    report_data = {
        "mission_id": result.idResult,
        "mission_name": result.MissionName,
        "robot_name": result.RobotName,
        "status": result.Status,
        "timestamp": result.Timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "details": result.Details,
        "operator": current_user.Username
    }
    return render_template('report/failed_report.html', report_data=report_data, result_id=result_id)