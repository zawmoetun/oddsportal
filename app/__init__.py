from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('configs/production.py')
#app.config.from_pyfile('configs/development.py')
db = SQLAlchemy(app)

from app import views
