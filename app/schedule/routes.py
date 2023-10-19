from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import _
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Schedule, Group, Subject, Classroom, Faculty
from app.schedule import bp
from app.schedule.forms import ScheduleForm, GroupForm, FacultyForm
from app.roles import schedule_editor_required
from app.api.schedule import weeks_split, academic_year_number, schedule_sort


@bp.route('/', methods=['GET', 'POST'])
@schedule_editor_required
def main():
    groups = [group for group in Group.query.all()]
    faculties = [faculty for faculty in Faculty.query.all()]

    return render_template('schedule/main.html',
                           groups=groups,
                           faculties=faculties,
                           title='Schedule')


@bp.route('/get_groups_by_faculty/<int:faculty_id>', methods=['GET'])
def get_groups_by_faculty(faculty_id):
    # Получите факультет по его ID
    faculty = Faculty.query.get(faculty_id)

    if faculty is None:
        return jsonify({'groups': []})

    # Используйте связь faculty.groups, чтобы получить группы, привязанные к факультету
    groups = faculty.groups

    # Создайте список групп для передачи обратно на клиентскую сторону
    groups_list = [{'id': group.id, 'name': group.name} for group in groups]

    return jsonify({'groups': groups_list})


@bp.route('/get_subgroups_by_group/<int:group_id>', methods=['GET'])
def get_subgroups_by_group(group_id):
    group = Group.query.get(group_id)

    if group:
        subgroups = group.subgroups.split(',') if group.subgroups else []
        subgroups_list = [{'id': int(subgroup), 'name': subgroup} for subgroup in subgroups]
    else:
        subgroups_list = []

    return jsonify({'subgroups': subgroups_list})


@bp.route('/create_faculty', methods=['GET', 'POST'])
def create_faculty():
    form = FacultyForm()

    if form.validate_on_submit():
        faculty = Faculty(name=form.name.data)
        db.session.add(faculty)
        db.session.commit()
        flash('Faculty created successfully', 'success')
        return redirect(url_for('schedule.create_faculty'))

    faculties = Faculty.query.all()

    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        group_name = request.form.get('group_name')
        faculty = Faculty.query.get(faculty_id)

        if faculty:
            group = Group(name=group_name, faculty=faculty)
            db.session.add(group)
            db.session.commit()
            flash('Group added successfully', 'success')

    return render_template('schedule/create_faculty.html',
                           form=form,
                           faculties=faculties)


@bp.route('/create_group/<int:faculty_id>', methods=['GET', 'POST'])
def create_group(faculty_id):

    form = GroupForm()

    group = None

    if form.validate_on_submit():
        name = form.name.data
        full_name = form.full_name.data
        subgroups = form.subgroups.data

        # Попробуйте найти существующую группу с заданным именем
        group = Group.query.filter_by(name=name).first()

        if group:
            # Если группа существует, обновите ее
            group.full_name = full_name
            group.subgroups = subgroups
            flash('Group updated successfully', 'success')
        else:
            # Если группа не существует, создайте новую
            group = Group(name=name,
                          full_name=full_name,
                          subgroups=subgroups,
                          faculty_id=faculty_id)
            db.session.add(group)
            flash('Group created successfully', 'success')

        db.session.commit()

        return redirect(url_for('schedule.create_faculty'))

    return render_template('schedule/create_group.html',
                           form=form,
                           group=group)


@bp.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    selected_group_id = request.args.get('selected_group_id')
    selected_group = Group.query.get(selected_group_id)

    selected_faculty_id = request.args.get('selected_faculty_id')
    selected_faculty = Faculty.query.get(selected_faculty_id)

    form = ScheduleForm()
    form.group.data = selected_group

    if selected_group is None:
        flash('Group not found', 'danger')
        return redirect(url_for('schedule.main'))

    # Подгружаем существующие значения для групп, дисциплин и аудиторий
    groups = [group for group in Group.query.all()]
    subjects = [subject for subject in Subject.query.all()]
    classrooms = [classroom for classroom in Classroom.query.all()]
    even_weeks = [(0, 'Все'), (1, 'Четные'), (2, 'Нечетные')]

    if selected_group.subgroups is not None and selected_group.subgroups != '':
        subgroups = [(0, 'Общее')] + [(int(subgroup), subgroup) for subgroup in selected_group.subgroups.split(',')]
    else:
        subgroups = [(0, 'Общее')]

    # if form.validate_on_submit():
    if request.method == 'POST':
        subject_name = form.subject.data
        classroom_name = form.classroom.data
        day_of_week = form.day_of_week.data
        lesson_number = form.lesson_number.data
        weeks = form.weeks.data
        is_lecture = form.is_lecture.data

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()

        classroom = Classroom.query.filter_by(name=classroom_name).first()
        if not classroom:
            classroom = Classroom(name=classroom_name)
            db.session.add(classroom)
            db.session.commit()

        # Извлекаем выбранную подгруппу из запроса
        selected_subgroup = int(request.form.get('subgroup', 0))
        selected_even_weeks = int(request.form.get('even_weeks', 0))

        schedule_entry = Schedule(
            group_id=selected_group_id,
            subgroup=selected_subgroup,
            subject_id=subject.id,
            classroom_id=classroom.id,
            day_of_week=day_of_week,
            lesson_number=lesson_number,
            weeks=','.join(weeks),  # сохраняем выбранные недели как строку
            even_weeks=selected_even_weeks,
            is_lecture=is_lecture
        )

        db.session.add(schedule_entry)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'SQLAlchemyError: {e}')

        return redirect(url_for('schedule.view_all_schedule'))

    return render_template('schedule/add_schedule.html',
                           form=form,
                           selected_group=selected_group,
                           groups=groups,
                           subjects=subjects,
                           classrooms=classrooms,
                           subgroups=subgroups,
                           selected_faculty=selected_faculty,
                           even_weeks=even_weeks)


@bp.route('/view_schedules', methods=['GET'])
def view_schedules():
    schedule_entries = Schedule.query.all()

    schedule_entries = schedule_sort(schedule_entries)

    # Проходим по всем записям и форматируем их недели
    schedule_entries = weeks_split(schedule_entries)

    return render_template('schedule/view_schedules.html',
                           schedule_entries=schedule_entries)


@bp.route('/view_current_schedule', methods=['GET', 'POST'])
@login_required
def view_current_schedule():
    user = current_user
    group_id = current_user.group_id
    academic_week = academic_year_number()

    if academic_week % 2 == 0:
        curr_week_even = 1
    else:
        curr_week_even = 2

    if not group_id:
        flash('You not have group')
        return redirect(url_for('schedule.select_group'))

    group = Group.query.get(group_id)
    schedule_entries = Schedule.query.filter_by(group=group).all()
    schedule_entries = schedule_sort(schedule_entries)

    user_schedule = []
    for entry in schedule_entries:
        if entry.subgroup == current_user.subgroup or entry.subgroup == 0:
            if str(academic_week) in entry.weeks:
                if curr_week_even == entry.even_weeks or entry.even_weeks == 0:
                    user_schedule.append(entry)

    # Проходим по всем записям и форматируем их недели
    user_schedule = weeks_split(user_schedule)

    return render_template('schedule/view_current_schedule.html',
                           schedule_entries=user_schedule,
                           user=user,
                           academic_week=academic_week,
                           title='Current Schedule')


@bp.route('/select_group', methods=['GET', 'POST'])
@login_required
def select_group():
    groups = [group for group in Group.query.all()]
    faculties = [faculty for faculty in Faculty.query.all()]

    return render_template('schedule/select_group.html',
                           groups=groups,
                           faculties=faculties,
                           title='Select Group')


@bp.route('/add_group_for_student', methods=['GET', 'POST'])
@login_required
def add_group_for_student():
    selected_faculty_id = request.args.get('selected_faculty_id')
    selected_group_id = request.args.get('selected_group_id')
    selected_subgroup = request.args.get('selected_subgroup')

    current_user.group_id = selected_group_id
    current_user.subgroup = selected_subgroup

    db.session.commit()

    return redirect(url_for('schedule.view_current_schedule'))


@bp.route('/delete_faculty/<int:faculty_id>', methods=['GET', 'POST'])
def delete_faculty(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)

    if not faculty:
        flash('Faculty not found', 'danger')
        return redirect(url_for('schedule.create_faculty'))

    # Заранее удаляем расписания для групп факультета
    for group in faculty.groups:
        db.session.query(Schedule).filter_by(group_id=group.id).delete()

    db.session.delete(faculty)
    db.session.commit()

    flash('Faculty deleted successfully', 'success')
    return redirect(url_for('schedule.create_faculty'))


@bp.route('/delete_group/<int:group_id>', methods=['GET', 'POST'])
def delete_group(group_id):
    group_entry = Group.query.get(group_id)

    if not group_entry:
        flash('Group not found', 'danger')
        return redirect(url_for('schedule.create_faculty'))

    db.session.delete(group_entry)
    db.session.commit()

    flash('Group deleted successfully', 'success')
    return redirect(url_for('schedule.create_faculty'))


@bp.route('/delete_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def delete_schedule(schedule_id):
    schedule_entry = Schedule.query.get(schedule_id)

    if not schedule_entry:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedule.view_all_schedule'))

    db.session.delete(schedule_entry)
    db.session.commit()

    flash('Schedule deleted successfully', 'success')
    return redirect(url_for('schedule.view_all_schedule'))


@bp.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule_entry = Schedule.query.get(schedule_id)

    if not schedule_entry:
        flash('Schedule not found', 'danger')
        return redirect(url_for('view_all_schedule'))

    selected_group_id = schedule_entry.group_id
    selected_group = Group.query.get(selected_group_id)
    selected_subgroup = schedule_entry.subgroup
    selected_even_weeks = schedule_entry.even_weeks

    form = ScheduleForm(group=schedule_entry.group_id,
                        subject=schedule_entry.subject_id,
                        classroom=schedule_entry.classroom_id,
                        day_of_week=schedule_entry.day_of_week,
                        lesson_number=schedule_entry.lesson_number,
                        weeks=schedule_entry.weeks,
                        is_lecture=schedule_entry.is_lecture)

    form.group.data = selected_group

    # Подгружаем существующие значения для групп, дисциплин и аудиторий
    groups = [group for group in Group.query.all()]
    subjects = [subject for subject in Subject.query.all()]
    classrooms = [classroom for classroom in Classroom.query.all()]
    even_weeks = [(0, 'Все'), (1, 'Четные'), (2, 'Нечетные')]

    if selected_group.subgroups is not None and selected_group.subgroups != '':
        subgroups = [(0, 'Общее')] + [(int(subgroup), subgroup) for subgroup in selected_group.subgroups.split(',')]
    else:
        subgroups = [(0, 'Общее')]

    if request.method == 'POST':
        subject_name = form.subject.data
        classroom_name = form.classroom.data
        day_of_week = form.day_of_week.data
        lesson_number = form.lesson_number.data
        weeks = form.weeks.data
        is_lecture = form.is_lecture.data

        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()

        classroom = Classroom.query.filter_by(name=classroom_name).first()
        if not classroom:
            classroom = Classroom(name=classroom_name)
            db.session.add(classroom)
            db.session.commit()

        selected_subgroup = int(request.form.get('subgroup', 0))
        selected_even_weeks = int(request.form.get('even_weeks', 0))

        schedule_entry.subject_id = subject.id
        schedule_entry.classroom_id = classroom.id
        schedule_entry.day_of_week = day_of_week
        schedule_entry.lesson_number = lesson_number
        schedule_entry.weeks = ','.join(weeks)
        schedule_entry.even_weeks = selected_even_weeks
        schedule_entry.is_lecture = is_lecture
        schedule_entry.subgroup = selected_subgroup

        db.session.commit()

        flash('Schedule updated successfully', 'success')
        return redirect(url_for('schedule.view_all_schedule'))

    return render_template('schedule/edit_schedule.html',
                           form=form,
                           schedule_entry=schedule_entry,
                           groups=groups,
                           subjects=subjects,
                           classrooms=classrooms,
                           subgroups=subgroups,
                           selected_subgroup=selected_subgroup,
                           selected_even_weeks=selected_even_weeks,
                           even_weeks=even_weeks)
