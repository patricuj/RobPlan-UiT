from flask import Blueprint

robot_status_bp = Blueprint('robot_status', __name__)

from . import views
