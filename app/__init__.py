from flask import Flask
from flask_cors import CORS
from .mqtt_client import MQTTClient
from config import Config
from .models import User 
from .extensions import db, login_manager, socketio, csrf, moment
from .models import Notification
from flask_login import current_user

def create_app():
    """
    Oppretter og konfigurerer Flask-applikasjonen.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiserer utvidelser med applikasjonen
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    csrf.init_app(app)
    moment.init_app(app)

    # Aktiverer CORS for alle ruter
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Setter opp innloggingsvisningen
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        """
        Laster en bruker fra databasen ved hjelp av bruker-ID.
        """
        return User.query.get(int(user_id))

    # Initialiserer og kobler til MQTT-klienten
    mqtt_client = MQTTClient('localhost', 1883, 'isar', None, socketio, app)
    mqtt_client.connect()

    # Registrerer blueprint for ulike moduler
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
        """
        Injiserer antall uleste notifikasjoner i konteksten.

        Returns:
            dict: En ordbok med antall uleste notifikasjoner.
        """
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                Users_idUser=current_user.idUser, IsRead=False
            ).count()
            adjusted_unread_count = int(unread_count / 2)
            return {'unread_count': adjusted_unread_count}
        return {}

    return app
