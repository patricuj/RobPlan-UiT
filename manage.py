import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    ssl_context = (
        os.getenv('SSL_CERT_PATH'), 
        os.getenv('SSL_KEY_PATH')
    )
    socketio.run(app, debug=True, port=5000, ssl_context=ssl_context)
