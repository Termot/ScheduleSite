from app import create_app, db
from app.models import User, Notification, Task, \
    Schedule, Group, Subject, Classroom

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'Notification': Notification, 'Task': Task,
            'Schedule': Schedule, 'Group': Group, 'Subject': Subject,
            'Classroom': Classroom}
