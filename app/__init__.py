
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_moment import Moment
from flask_login import LoginManager 
from datetime import datetime

app = Flask(__name__) 
db = SQLAlchemy() 
login_manager = LoginManager()
#moment = Moment()

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    
    app.config['SECRET_KEY'] = 'CoachView123' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' 
    login_manager.login_message_category = 'info'
    
    from app.models import Player, Match
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    # from app import errors, se for ter um arquivo para tratamento de erros

    with app.app_context():
        db.create_all() 

    return app, db
