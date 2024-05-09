from flask import Flask
from .mqtt_client import MQTTClient
from config import Config
from .models import User 
from .extensions import db, login_manager, socketio, csrf, moment
from .models import Notification
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    csrf.init_app(app)
    moment.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) 

    mqtt_client = MQTTClient('localhost', 1883, 'isar', None, socketio, app)
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

    from .settings import settings_bp
    app.register_blueprint(settings_bp)
    
    from .notifications import notifications_bp
    app.register_blueprint(notifications_bp)

    @app.context_processor
    def inject_unread_count():
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                Users_idUser=current_user.idUser, IsRead=False
            ).count()
            adjusted_unread_count = int(unread_count / 2)
            return {'unread_count': adjusted_unread_count}
        return {}

    return app
