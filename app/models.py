from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    
    idUser = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(45), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def get_id(self):
        return str(self.idUser) 

class Notification(db.Model):
    __tablename__ = 'Notifications'
    
    idNotifications = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(100), nullable=False)
    Severity = db.Column(db.String(100), nullable=False)
    Message = db.Column(db.Text, nullable=False)
    Details = db.Column(db.Text, nullable=True)
    Timestamp = db.Column(db.DateTime, nullable=False)
    IsRead = db.Column(db.Boolean, nullable=False, default=False)
    Users_idUser = db.Column(db.Integer, db.ForeignKey('Users.idUser'), nullable=False)
    isar_id = db.Column(db.String(36), nullable=True)


class Mission(db.Model):
    __tablename__ = 'Missions'

    idMission = db.Column(db.Integer, primary_key=True)
    MissionName = db.Column(db.String(255), nullable=False)
    MissionData = db.Column(db.Text, nullable=False)
    IsAvailable = db.Column(db.Boolean, nullable=False, default=True)
    Port = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(255), nullable=True, default='Ingen planlagt inspeksjon')
    LastCompleted = db.Column(db.DateTime, nullable=True)
    Deadline = db.Column(db.DateTime, nullable=True)


class Result(db.Model):
    __tablename__ = 'Results'

    idResult = db.Column(db.Integer, primary_key=True)
    MissionName = db.Column(db.String(255), nullable=False)
    RobotName = db.Column(db.String(255), nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    Timestamp = db.Column(db.DateTime, nullable=False)
    Details = db.Column(db.Text, nullable=True)


class RobotInfo(db.Model):
    __tablename__ = 'RobotInfo'
    
    id = db.Column(db.Integer, primary_key=True)
    isar_id = db.Column(db.String(36), nullable=False)
    robot_name = db.Column(db.String(50), nullable=False)
    battery_level = db.Column(db.Float)
    robot_status = db.Column(db.String(20))
    current_mission_id = db.Column(db.String(50))
    port = db.Column(db.Integer)