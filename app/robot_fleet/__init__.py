from flask import Blueprint

robot_fleet_bp = Blueprint('robot_fleet', __name__)

from . import views
