import os
from app import create_app, socketio
from dotenv import load_dotenv

# Laster inn miljøvariabler fra .env-filen
load_dotenv()

# Oppretter Flask-applikasjonen
app = create_app()

if __name__ == '__main__':
    """
    Kjører Flask-applikasjonen med SocketIO-støtte og SSL-konfigurasjon.
    """
    # Henter SSL-sertifikat og nøkkelstier fra miljøvariabler
    ssl_context = (
        os.getenv('SSL_CERT_PATH'), 
        os.getenv('SSL_KEY_PATH')
    )
    
    # Starter applikasjonen på port 5000
    socketio.run(app, debug=True, port=5000, ssl_context=ssl_context)
