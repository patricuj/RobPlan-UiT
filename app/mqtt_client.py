import paho.mqtt.client as mqtt
import json


class MQTTClient:
    def __init__(self, host, port, username=None, password=None, socketio=None):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socketio = socketio 
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
        self.client.subscribe(topics)


    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        payload = msg.payload.decode()
        topic_parts = msg.topic.split('/')
        isar_id = topic_parts[1]
        info_type = topic_parts[2]
        data = json.loads(payload)

        if info_type in ['robot_status', 'robot_info', 'mission', 'robot_heartbeat']:
            if info_type == 'robot_heartbeat':
                self.socketio.emit('update_robot_heartbeat', {
                    'data': payload, 
                    'isar_id': isar_id, 
                    'robot_name': data.get('robot_name', 'Unknown'),
                    'timestamp': data.get('timestamp', None)
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
            self.socketio.emit('update_battery', {
                'data': payload, 
                'isar_id': isar_id
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