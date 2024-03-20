# built in import for environment variables
import os
# external imports for flask application and exceptions
from flask import Flask
from marshmallow.exceptions import ValidationError
# local imports for app libraries
from init import db, ma, jwt, bcrypt


def create_app():
    # create instance of flask to establish 
    # applications root path
    app = Flask(__name__)
    # configure environment variables
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")
    # initialise app extensions 
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    # implement global error handling 
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
    # register blueprints for controllers 
    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)

    from controllers.user_controller import user_bp
    app.register_blueprint(user_bp)

    from controllers.media_controller import media_bp
    app.register_blueprint(media_bp)

    from controllers.interaction_controller import interaction_bp
    app.register_blueprint(interaction_bp)

    from controllers.comment_controller import comment_bp
    app.register_blueprint(comment_bp)
    # return app instance
    return app
