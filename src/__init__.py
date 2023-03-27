from flask import Flask
import os

from src.users import users
from src.accounts import account
from src.models import db

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if(test_config is None):
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI')
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    
    with app.app_context():    
        db.create_all()
    app.register_blueprint(users)
    app.register_blueprint(account)
    return app





