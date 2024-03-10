import os

from flask import Flask, Blueprint, request
from dotenv import load_dotenv

from init import db, ma, jwt, bcrypt


load_dotenv()
main_bp = Blueprint('main', __name__, url_prefix='/main')

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
    
    app.register_blueprint(main_bp)


    return app


@main_bp.route("/")
def greeting():
    return {"message": "Hello World!!"}, 200
