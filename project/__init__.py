from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user
from flask_migrate import Migrate
import os
from linebot import (
    LineBotApi, WebhookHandler
)


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_url_path='/static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'none')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost:5432/flasknote"

    YOUR_CHANNEL_ACCESS_TOKEN = os.getenv("YOUR_CHANNEL_ACCESS_TOKEN", 'none')
    YOUR_CHANNEL_SECRET = os.getenv("YOUR_CHANNEL_SECRET", 'none')

    line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(YOUR_CHANNEL_SECRET)

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'line.index'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def error_404(error):
        logout_user()
        return render_template('error_handlers/404.html'), 404

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .line import line as line_blueprint
    app.register_blueprint(line_blueprint)

    return app
