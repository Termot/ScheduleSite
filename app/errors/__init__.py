from flask import Blueprint

bp = Blueprint('errors', __name__)

# Импорт внизу для избежания циклических зависимостей !!!
from app.errors import handlers
