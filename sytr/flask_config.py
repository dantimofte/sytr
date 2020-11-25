from pathlib import Path


class Config:
    __ROOT_PATH = Path(__file__).resolve().parent
    DEBUG = False
    TESTING = False
    # import os;os.urandom(24)
    SECRET_KEY = b"^\xec\x9a\x15\x0eL\xec?I|'\x048\x1e\x82$\xd5\xe5\x87q\x98\xd3\x0c\xd1"
    ROOT_PATH = __ROOT_PATH
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE')


class ProductionConfig(Config):
    DATABASE_URI = ''  # MySQL, PostgreSQL, MariaDB, etc.


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    ENV = 'development'


class TestingConfig(Config):
    TESTING = True
