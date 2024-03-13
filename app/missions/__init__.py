from flask import Blueprint

missions_bp = Blueprint('missions', __name__)

from . import views
