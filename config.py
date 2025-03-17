import os


class Config(object):
    DEBUG = True
    MASTER_DB_URL = "mysql+pymysql://flask_user:flask_password@localhost/mydatabase"
    SQLALCHEMY_DATABASE_URI = MASTER_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

