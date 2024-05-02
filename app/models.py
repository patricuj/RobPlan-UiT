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