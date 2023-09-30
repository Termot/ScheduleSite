from app import db, create_app
from app.models import ScheduleHelper, Weeks, Couple, Group, Discipline, Auditory


def add_schedule_to_db(s_dict):
    table_weeks = Weeks(weeks=s_dict['weeks'])
    table_couple = Couple(couple=s_dict['couple'])
    table_group = Group(group=s_dict['group'])
    table_discipline = Discipline(discipline=s_dict['discipline'])
    table_auditory = Auditory(auditory=s_dict['auditory'])

    s_helper = ScheduleHelper()

    s_helper.weeks.append(table_weeks)
    s_helper.couple.append(table_couple)
    s_helper.group.append(table_group)
    s_helper.discipline.append(table_discipline)
    s_helper.auditory.append(table_auditory)

    db.session.add(s_helper)
    db.session.commit()

    print(s_helper)

    schedules = ScheduleHelper.query.all()

    for s in schedules:
        print(f'''
        id: {s.id}
        "{s.weeks}"
        "{s.couple}"
        "{s.group}"
        "{s.discipline}"
        "{s.auditory}"''')


def add_data_to_tables():
    weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    couples = [1, 2, 3, 4, 5, 6]
    groups = ['Г-301/1', 'Г-301/2']
    disciplines = ['Математика', 'Геодезия', 'Русский', 'Английский']
    auditories = ['323/2', '103/4', '234/1', '456/3']

    for w in weeks:
        add_w = Weeks(weeks)
        db.session.add()


def test():
    s_dict = {}
    s_dict['dotw'] = 'Понедельник'
    s_dict['weeks'] = '1-3'
    s_dict['couple'] = 1
    s_dict['group'] = 'Г-301'
    s_dict['discipline'] = 'Математика'
    s_dict['auditory'] = '312/3'

    add_schedule_to_db(s_dict)


def see_db():
    schedules = ScheduleHelper.query.all()

    for s in schedules:
        print(f'')


app = create_app()
app.app_context().push()

with app.app_context():
    see_db()