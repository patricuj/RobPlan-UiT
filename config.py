import secrets

class Config:
    
    SECRET_KEY = secrets.token_urlsafe(16)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:test@localhost/myDb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass