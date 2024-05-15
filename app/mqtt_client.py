import paho.mqtt.client as mqtt
import json
from .extensions import db
from datetime import datetime
from .models import Notification, Result

class MQTTClient:
    def __init__(self, host, port, username=None, password=None, socketio=None, app=None):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socketio = socketio
        self.app = app 
        if self.username and self.password:
            self.client.username_pw_set(username, password)

    def on_connect(self, client, userdata, flags, rc):
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

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        payload = msg.payload.decode()
        topic_parts = msg.topic.split('/')
        isar_id = topic_parts[1]
        info_type = topic_parts[2]
        data = json.loads(payload)
        mission_status = None
        
        if info_type in ['robot_status', 'robot_info', 'mission', 'robot_heartbeat']:
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
                    self.socketio.emit(f'update_{info_type}', {
                        'data': payload, 
                        'isar_id': isar_id, 
                        'robot_name': data.get('robot_name', 'Unknown'),
                        'current_mission_id': data.get('mission_id', None),
                        'status': data.get('status', None),
                        'timestamp': data.get('timestamp', None)
                    })
        elif info_type == 'battery':
            battery_level = data['battery_level']
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

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port)
        self.client.loop_start()


def create_database_notification(app, data, isar_id):
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
