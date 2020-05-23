import os


base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you-will-never-guess"
    SQL_DB_URI = os.environ.get('DATABASE_URL') or os.path.join(base_dir, 'data', 'pypatch.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQL_DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
