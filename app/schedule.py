from app import db, create_app
from app.models import Schedule, Group, Subject, Classroom, Faculty


def create_faculty_and_group(faculty_name, group_name, subgroups):
    faculty_id = Faculty.query.filter_by(name=faculty_name).first().id
    if not faculty_id:
        db.session.add(Faculty(name=faculty_name))
        db.session.commit()
        print(f'Create faculty "{faculty_name}"')

    group = Group.query.filter_by(name=group_name).first()
    if not group:
        db.session.add(Group(name=group_name,
                             subgroups=subgroups,
                             faculty_id=faculty_id))
        db.session.commit()
        print(f'Create group "{group_name}" with subgroups "{subgroups}"')


def create_schedule(group_name: str,
                    subgroup: int,
                    subject_name: str,
                    classroom_name: str,
                    day_of_week: str,
                    lesson_number: int,
                    weeks: str,
                    even_weeks: int,
                    is_lecture: bool):

    # Получение существующих объектов группы, дисциплины и аудитории или их создание
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(name=group_name)
        db.session.add(group)

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        subject = Subject(name=subject_name)
        db.session.add(subject)

    classroom = Classroom.query.filter_by(name=classroom_name).first()
    if not classroom:
        classroom = Classroom(name=classroom_name)
        db.session.add(classroom)

    schedule_entry = Schedule(
        group_id=group.id,  # int
        subgroup=subgroup,  # int
        subject_id=subject.id,  # int
        classroom_id=classroom.id,  # int
        day_of_week=day_of_week,  # str
        lesson_number=lesson_number,  # int
        weeks=weeks,  # str
        even_weeks=even_weeks,
        is_lecture=is_lecture  # bool
    )
    db.session.add(schedule_entry)
    db.session.commit()

    print('Schedule was added')


def main():
    faculty_name = 'Природопользование и строительство'
    group_name = 'Г-301'
    subgroups = '1,2'

    create_faculty_and_group(faculty_name, group_name, subgroups)

    create_schedule(group_name=group_name,
                    subgroup=2,
                    subject_name='дисциплина',
                    classroom_name='319/2',
                    day_of_week='Понедельник',
                    lesson_number=1,
                    weeks='10,11,12,13,14,15,16',
                    even_weeks=0,
                    is_lecture=False)


app = create_app()
app.app_context().push()

with app.app_context():
    '''Здесь вызываем функцию для добавления чего-то в базу данных'''
    main()
