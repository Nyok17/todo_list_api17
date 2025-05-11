from flask import Flask
from config import Config
from models import db
from routes import auth_bp, todo_bp
from extensions import bcrypt, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    #Initialize the extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)