import os
import click
from flask import Blueprint

"""
Использовать команды так:
flask translate update <-- обновить все языки после внесения изменений в маркеры _() и _l()
flask translate compile <-- компилировать все языки после обновления файлов перевода
flask translate init <language-code> <-- добавить новый язык (без <>) (es - испанский)
"""

bp = Blueprint('translate', __name__)

@bp.cli.command('update')
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

@bp.cli.command('compile')
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')

@bp.cli.command('init')
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')