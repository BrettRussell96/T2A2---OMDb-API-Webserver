from datetime import date

from flask import Blueprint

from init import db, bcrypt
from models.user import User

db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created")


@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables dropped")


@db_commands.cli.command('seed')
def seed_tables():
    print("Tables seeded")
