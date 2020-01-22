from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from flask_socketio import SocketIO, emit

import pymysql
import os
import boto3

app = Flask(__name__)

xray_recorder.configure(service="My application", daemon_address="xray:2000")
XRayMiddleware(app, xray_recorder)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://"+os.getenv("MYSQL_USER")+":"+os.getenv("MYSQL_PASSWORD")+"@"+os.getenv("MYSQL_HOST")+"/"+os.getenv("MYSQL_DB")
db = SQLAlchemy(app)

s3 = boto3.resource("s3", aws_access_key_id=os.getenv("ACCESS_ID"), aws_secret_access_key=os.getenv("ACCESS_SECRET_ID"))

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
#socketio = SocketIO(app)

from application import routes
