from flask import render_template, jsonify
from . import robot_fleet_bp
from ..models import RobotInfo
from sqlalchemy.sql import func
from ..extensions import db
from flask_login import login_required

@robot_fleet_bp.route('/robot_fleet')
@login_required
def robot_fleet():
    """
    Viser oversikt over robotflåten.
    """
    robots = RobotInfo.query.all()
    return render_template('/robot_fleet/robot_fleet.html', robots=robots)


@robot_fleet_bp.route('/api/robot_info', methods=['GET'])
@login_required
def get_latest_robot_info():
    """
    Henter den nyeste informasjonen om robotene fra databasen
    """
    # Oppretter en delspørring for å finne det siste RobotInfo-IDen for hver isar_id
    subquery = db.session.query(
        RobotInfo.isar_id,
        func.max(RobotInfo.id).label('latest_id')
    ).group_by(RobotInfo.isar_id).subquery()

    # Bruker delspørringen for å hente de nyeste oppføringene fra RobotInfo-tabellen
    latest_records = db.session.query(RobotInfo).join(
        subquery, RobotInfo.id == subquery.c.latest_id
    ).all()

    # Liste for å lagre den nyeste informasjonen om hver robot
    robot_data = []
    
    # Iterer gjennom de nyeste oppføringene
    for robot in latest_records:
        battery_level = robot.battery_level
        if battery_level is None:
            # Hvis batterinivået ikke er tilgjengelig, finner vi den forrige tilgjengelige verdien på batterinivå
            previous_battery = db.session.query(RobotInfo.battery_level).filter(
                RobotInfo.isar_id == robot.isar_id,
                RobotInfo.battery_level != None
            ).order_by(RobotInfo.id.desc()).first()
            battery_level = previous_battery[0] if previous_battery else 0

        # Legger til robotens data i listen
        robot_data.append({
            'isar_id': robot.isar_id,
            'robot_name': robot.robot_name,
            'battery_level': battery_level,
            'robot_status': robot.robot_status,
            'current_mission_id': robot.current_mission_id
        })
    
    # Returner den nyeste informasjonen som JSON
    return jsonify(robot_data)
