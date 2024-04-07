from flask import Blueprint

report_bp = Blueprint('report', __name__)

from . import views