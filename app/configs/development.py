import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://soccer:soccer@localhost/soccer_db"

CSRF_ENABLED = True
SECRET_KEY = 'you shall not pass'
