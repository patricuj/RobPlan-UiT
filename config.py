import secrets

class Config:
    """
    Konfigurasjonsklasse for å sette opp Flask-applikasjonen.

    Attributter:
        SECRET_KEY (str): En sikker nøkkel for sesjonshåndtering og andre sikkerhetsrelaterte formål.
        SQLALCHEMY_DATABASE_URI (str): URI for tilkobling til en MySQL-database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Deaktiverer SQLAlchemy modifikasjonssporing for å forbedre ytelsen.
    """
    
    # Genererer en sikker nøkkel for applikasjonen
    SECRET_KEY = secrets.token_urlsafe(16)
    
    # Database tilkoblings-URI ved bruk av pymysql for MySQL-database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:test@localhost/myDb'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        """
        Initialiserer applikasjonen med den gitte konfigurasjonen.
        """
        pass

# Denne koden er hentet fra et tidligere prosjekt med navn QuizMaster16 skrevet av Dennis Mai. Fra faget DTE-2509 Databaser og webapplikasjoner 1, våren 2023.