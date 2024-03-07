from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from psycopg2 import errorcodes