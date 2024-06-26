import paho.mqtt.client as mqtt
import json
from .extensions import db
from datetime import datetime, timedelta
from .models import Notification, Result, RobotInfo

class MQTTClient:
    """
    MQTT-klient for å håndtere meldinger fra en MQTT-broker og oppdatere
    databasemodeller samt sende oppdateringer til klienter via SocketIO.
    """

    def __init__(self, host, port, username=None, password=None, socketio=None, app=None):
        """
        Initialiserer MQTTClient med nødvendige parametre.

        Args:
            host (str): Vert for MQTT-broker.
            port (int): Port for MQTT-broker.
            username (str, optional): Brukernavn for MQTT-broker. Default er None.
            password (str, optional): Passord for MQTT-broker. Default er None.
            socketio (SocketIO, optional): SocketIO-objekt for sanntidskommunikasjon. Default er None.
        """
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socketio = socketio
        self.app = app
        self.status_timers = {}
        if self.username and self.password:
            self.client.username_pw_set(username, password)

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback-funksjon for tilkobling til MQTT-broker.
        Abonnerer på topics hos ISAR.
        """
        print(f"Connected with result code {rc}")
        topics = [
            ("isar/+/robot_heartbeat", 0),
            ("isar/+/robot_status", 0),
            ("isar/+/battery", 0),
            ("isar/+/robot_info", 0),
            ("isar/+/mission", 0),
            ("isar/+/pose", 0),
            ("isar/+/inspection_result", 0),
        ]
        for topic in topics:
            self.client.subscribe(topic)

        self.delete_old_robot_info(seconds=60)

    def on_message(self, client, userdata, msg):
        """
        Callback-funksjon for mottatte meldinger fra MQTT-broker.
        """
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        payload = msg.payload.decode()
        topic_parts = msg.topic.split('/')
        isar_id = topic_parts[1]
        info_type = topic_parts[2]
        data = json.loads(payload)

        if info_type == 'robot_info':
            port = data.get('port')
            self.update_robot_info(isar_id, data['robot_name'], port=port)
        elif info_type == 'battery':
            battery_level = data['battery_level']
            if battery_level is not None:
                self.update_robot_info(isar_id, data['robot_name'], battery_level=battery_level)
                self.socketio.emit('update_battery', {
                    'data': payload, 
                    'isar_id': isar_id
                })
                if battery_level < 60:
                    create_database_notification(self.app, data, isar_id)
                    self.socketio.emit('low_battery_warning', {
                        'robot_name': data.get('robot_name', 'Ukjent robot'),
                        'battery_level': battery_level,
                        'severity': 'High'
                    })
        elif info_type in ['robot_status', 'mission', 'robot_heartbeat']:
            if info_type == 'robot_heartbeat':
                self.socketio.emit('update_robot_heartbeat', {
                    'data': payload, 
                    'isar_id': isar_id, 
                    'robot_name': data.get('robot_name', 'Unknown'),
                    'timestamp': data.get('timestamp', None)
                })
            elif info_type == 'mission':
                mission_status = data.get('status', None)
                self.socketio.emit(f'update_{info_type}', {
                    'data': payload,
                    'isar_id': isar_id,
                    'robot_name': data.get('robot_name', 'Unknown'),
                    'current_mission_id': data.get('mission_id', None),
                    'status': mission_status,
                    'timestamp': data.get('timestamp', None)
                })
                if mission_status == 'successful':
                    create_mission_completion_notification(self.app, data.get('mission_id'), data.get('robot_name'))
                    self.socketio.emit('mission_completed', {
                        'robot_name': data.get('robot_name', 'Unknown'),
                        'mission_id': data.get('mission_id'),
                        'severity': 'Low'
                    })
                elif mission_status == 'failed':
                    error_description = data.get('error_description', 'Ukjent feil')
                    create_mission_failed_notification(self.app, data.get('mission_id'), data.get('robot_name'), error_description, isar_id)
                    self.socketio.emit('mission_failed', {
                        'robot_name': data.get('robot_name', 'Unknown'),
                        'mission_id': data.get('mission_id'),
                        'error_description': error_description,
                        'severity': 'High'
                    })
            else:
                if data.get('robot_status') or data.get('current_mission_id'):
                    self.update_robot_info(isar_id, data['robot_name'], robot_status=data.get('robot_status'), current_mission_id=data.get('current_mission_id'))
                self.socketio.emit(f'update_{info_type}', {
                    'data': payload, 
                    'isar_id': isar_id, 
                    'robot_name': data.get('robot_name', 'Unknown'),
                    'current_mission_id': data.get('mission_id', None),
                    'status': data.get('status', None),
                    'timestamp': data.get('timestamp', None)
                })
        elif info_type == 'pose':
            self.socketio.emit('update_pose', {
                'data': payload,
                'isar_id': isar_id,
                'robot_name': data.get('robot_name', 'Unknown'),
                'position': data.get('pose', {}).get('position', {}),
                'timestamp': data.get('timestamp', None)
            })
        elif info_type == 'inspection_result':
            self.socketio.emit('update_inspection_result', {
                'data': payload,
                'isar_id': isar_id,
                'robot_name': data.get('robot_name', 'Unknown'),
                'inspection_id': data.get('inspection_id', None),
                'inspection_path': data.get('inspection_path', None),
                'analysis_type': data.get('analysis_type', []),
                'timestamp': data.get('timestamp', None)
            })

    def update_robot_info(self, isar_id, robot_name, battery_level=None, robot_status=None, current_mission_id=None, port=None):
        """
        Oppdaterer robotinformasjon i databasen.
        """
        with self.app.app_context():
            latest_robot_info = RobotInfo.query.filter_by(isar_id=isar_id, robot_name=robot_name).order_by(RobotInfo.id.desc()).first()
            
            if latest_robot_info:
                if battery_level is None:
                    battery_level = latest_robot_info.battery_level
                if robot_status is None:
                    robot_status = latest_robot_info.robot_status
                if port is None:
                    port = latest_robot_info.port

                if robot_status == 'busy' and current_mission_id is None:
                    last_mission_info = RobotInfo.query.filter(
                        RobotInfo.isar_id == isar_id,
                        RobotInfo.robot_name == robot_name,
                        RobotInfo.current_mission_id != None
                    ).order_by(RobotInfo.id.desc()).first()
                    if last_mission_info:
                        current_mission_id = last_mission_info.current_mission_id

            if latest_robot_info:
                db.session.delete(latest_robot_info)
                db.session.commit()
            
            new_robot_info = RobotInfo(
                isar_id=isar_id,
                robot_name=robot_name,
                battery_level=battery_level,
                robot_status=robot_status,
                current_mission_id=current_mission_id,
                port=port if port is not None else (latest_robot_info.port if latest_robot_info else None),
                timestamp=datetime.utcnow(),
            )
            db.session.add(new_robot_info)
            db.session.commit()

    def delete_old_robot_info(self, seconds=60):
        """
        Sletter gamle RobotInfo-oppføringer fra databasen etter en viss tid.
        """
        with self.app.app_context():
            threshold_date = datetime.utcnow() - timedelta(seconds=seconds)
            print(f"Sletter oppføringer eldre enn: {threshold_date}")
            
            deleted = RobotInfo.query.filter(RobotInfo.timestamp < threshold_date).delete()
            db.session.commit()
            
            print(f"Antall slettede oppføringer: {deleted}")


    def connect(self):
        """
        Kobler til MQTT-broker og starter mottak av meldinger.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port)
        self.client.loop_start()

def create_database_notification(app, data, isar_id):
    """
    Oppretter en varsling i databasen for lavt batterinivå.
    """
    with app.app_context():
        message = f"Batterinivå lavt for robot {data.get('robot_name', 'Ukjent')} med batteriprosent: {data.get('battery_level')}%"
        new_notification = Notification(
            Users_idUser=1,
            Message=message,
            Type='Batterivarsel',
            Severity='High',
            Details='',
            Timestamp=datetime.utcnow(),
            IsRead=False
        )
        db.session.add(new_notification)
        db.session.commit()

def create_mission_completion_notification(app, mission_id, robot_name):
    """
    Oppretter en varsling i databasen når et oppdrag er fullført.
    """
    with app.app_context():
        message = f"{robot_name} har fullført oppdraget {mission_id}."
        new_notification = Notification(
            Users_idUser=1,
            Message=message,
            Type='Oppdragsstatus',
            Severity='Low',
            Details='',
            Timestamp=datetime.utcnow(),
            IsRead=False
        )
        db.session.add(new_notification)
        db.session.commit()

def create_mission_failed_notification(app, mission_id, robot_name, error_description, isar_id):
    """
    Oppretter en varsling i databasen når et oppdrag feiler.
    """
    with app.app_context():
        message = f"{robot_name} mislyktes med oppgaven {mission_id}. {error_description}"
        new_notification = Notification(
            Users_idUser=1,
            Message=message,
            Type='Oppdragsstatus',
            Severity='High',
            Details='',
            Timestamp=datetime.utcnow(),
            IsRead=False,
            isar_id=isar_id
        )
        db.session.add(new_notification)
        
        new_result = Result(
            MissionName=mission_id,
            RobotName=robot_name,
            Status='failed',
            Timestamp=datetime.utcnow(),
            Details=error_description
        )
        db.session.add(new_result)
        db.session.commit()

