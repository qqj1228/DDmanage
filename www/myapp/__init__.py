# myapp/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)

app.config.from_object('config.default')
app.config.from_object('config.user')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = '请登陆后再访问目标页面'
login_manager.init_app(app)

from . import views, apis, models, APIError
