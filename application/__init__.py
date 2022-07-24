from flask import Flask
from flask_socketio import SocketIO,join_room
from config import Config

app = Flask(__name__)

socketio = SocketIO(app)

from application import routes
