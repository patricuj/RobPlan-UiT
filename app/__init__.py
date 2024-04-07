from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from .mqtt_client import MQTTClient

csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    socketio.init_app(app)

    mqtt_client = MQTTClient('localhost', 1883, 'isar', None, socketio)
    mqtt_client.connect()
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .missions import missions_bp
    app.register_blueprint(missions_bp)

    from .robot_fleet import robot_fleet_bp
    app.register_blueprint(robot_fleet_bp)

    from .robot_status import robot_status_bp
    app.register_blueprint(robot_status_bp)

    from .history import history_bp
    app.register_blueprint(history_bp)

    from .report import report_bp
    app.register_blueprint(report_bp)

    return app
