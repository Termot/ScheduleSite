from app import create_app, db
from app.models import User, Notification, Task, \
    Schedule, Group, Subject, Classroom, Role

app = create_app()

with app.app_context():
    # Проверяем, есть ли уже роли в базе данных
    admin_role = Role.query.filter_by(name='Admin').first()
    user_role = Role.query.filter_by(name='User').first()
    schedule_editor_role = Role.query.filter_by(name='ScheduleEditor').first()

    if not admin_role:
        admin_role = Role(name='Admin', description='Admin role')
        db.session.add(admin_role)

    if not user_role:
        user_role = Role(name='User', description='Regular user role')
        db.session.add(user_role)

    if not schedule_editor_role:
        schedule_editor_role = Role(name='ScheduleEditor',
                                    description='Schedule editor role')
        db.session.add(schedule_editor_role)

    db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'Notification': Notification, 'Task': Task,
            'Schedule': Schedule, 'Group': Group, 'Subject': Subject,
            'Classroom': Classroom, 'Role': Role}
