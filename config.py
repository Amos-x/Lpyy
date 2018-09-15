# __author__ = "Amos"
# Email: 379833553@qq.com
"""
    Lpyy.config
    ~~~~~~~~~~~~~~~~~

    Lpyy project setting file

"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Gunicorn workers, default 4
    # WORKERS = 4

    # Django security setting, if your disable debug model, you should setting that
    ALLOWED_HOSTS = ['*']

    # Development env open this, when error occur display the full process track, Production disable it
    DEBUG = True

    # DEBUG, INFO, WARNING, ERROR, CRITICAL can set. See https://docs.djangoproject.com/en/1.10/topics/logging/
    LOG_LEVEL = 'DEBUG'
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

    # Database setting, Support sqlite3, mysql, postgres ....
    # See https://docs.djangoproject.com/en/1.10/ref/settings/#databases

    # SQLite setting:
    # DB_ENGINE = 'sqlite3'
    # DB_NAME = os.path.join(BASE_DIR, 'data', 'db.sqlite3')

    # MySQL or postgres setting like:
    DB_ENGINE = 'mysql'
    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = 'wyx379833553'
    DB_NAME = 'lpyy'

    # EMAIL SMTP settings:
    EMAIL_HOST = 'smtp.exmail.qq.com'
    EMAIL_PORT = 465
    EMAIL_HOST_USER = 'creatson@creatson.com'
    EMAIL_HOST_PASSWORD = 'Krs201705'
    EMAIL_USE_SSL = True
    EMAIL_SUBJECT_PREFIX = 'Operation'

    # When Django start it will bind this host and port
    # ./manage.py runserver 127.0.0.1:8080
    HTTP_BIND_HOST = '0.0.0.0'
    HTTP_LISTEN_PORT = 8000

    # Use Redis as cache broker for web socket
    # only choose one, Signgle Instance or Server Cluster?
    # Single Instance
    REDIS_CACHE_LOCATION = "redis://:wyx379833553@127.0.0.1:6379/6",   # redis单实例连接
    # Server Cluster , server port not sentinel port.
    # REDIS_CACHE_LOCATION = [
    #     "redis://192.168.9.80:6379/10",
    #     "redis://192.168.9.80:6380/10",
    #     "redis://192.168.9.80:6381/10",
    # ],

    # Redis max connections for connect pool
    REDIS_MAX_CONNECTIONS = 100

    # User redis as broker for celery
    CELERY_BROKER_URL = 'redis://:wyx379833553@127.0.0.1:6379/5'
    # User reids sentinel cluster
    # CELERY_BROKER_URL = 'sentinel://192.168.9.80:16379;sentinel://192.168.9.80:16380;sentinel://192.168.9.80:16381'

    def __init__(self):
        pass

    def __getattr__(self, item):
        return None


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


# # Default using Config settings, you can write if/else for different env
config = DevelopmentConfig()

