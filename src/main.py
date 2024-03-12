import os

from flask import Flask
from marshmallow.exceptions import ValidationError

from init import db, ma, jwt, bcrypt


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    @app.errorhandler(400)
    def bad_request(err):
        return {"error": str(err)}, 400

    @app.errorhandler(401)
    def unauthorized(err):
        return {"error": str(err)}, 401

    @app.errorhandler(404)
    def not_found(err):
        return {"error": str(err)}, 404

    @app.errorhandler(500)
    def internal_server_error(err):
        return {"error": str(err)}, 500
    
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return {"error": error.messages}, 400

    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)

    from controllers.user_controller import user_bp
    app.register_blueprint(user_bp)

    from controllers.media_controller import media_bp
    app.register_blueprint(media_bp)

    return app
