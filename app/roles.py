from flask import redirect, url_for
from flask_login import current_user

from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Admin':
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def schedule_editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'ScheduleEditor':
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

