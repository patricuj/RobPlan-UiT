from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .missions import missions_bp
    app.register_blueprint(missions_bp)

    from .robot_fleet import robot_fleet_bp
    app.register_blueprint(robot_fleet_bp)


    return app