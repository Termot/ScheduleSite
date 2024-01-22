from app import create_app, db
from app.models import User, Notification, Task, \
    Schedule, Group, Subject, Classroom, Role

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role,
            'Notification': Notification, 'Task': Task,
            'Schedule': Schedule, 'Group': Group, 'Subject': Subject,
            'Classroom': Classroom}
