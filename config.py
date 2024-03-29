import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    TEMPLATES_AUTO_RELOAD = True  # при изменении html не надо перезапускать flask

    SECRET_KEY = os.environ.get('SECRET_KEY') or '923r2dkk23-idwkkaii093-#904T%$(*&'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Почта
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'termometronator@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'elwmmxuzncjbgdfa'

    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'termometronator@gmail.com'
    # MAIL_PASSWORD = 'elwmmxuzncjbgdfa'

    ADMINS = ['termometronator@gmail.com', 'slowlii80085@gmail.com']

    # Количество постов на одной странице
    POSTS_PER_PAGE = 5

    # Языки перевода сайта
    LANGUAGES = ['ru', 'en']
    BABEL_DEFAULT_LOCALE = 'ru'

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'