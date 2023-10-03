from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import _
from flask_login import login_required
from app import db
from app.models import Schedule, Group, Subject, Classroom, Faculty
from app.schedule import bp
from app.schedule.forms import ScheduleForm, GroupForm, FacultyForm


@bp.route('/', methods=['GET', 'POST'])
def main():
    groups = [group for group in Group.query.all()]
    faculties = [faculty for faculty in Faculty.query.all()]

    return render_template('schedule/main.html',
                           groups=groups,
                           faculties=faculties)


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

    return render_template('schedule/create_faculty.html', form=form, faculties=faculties)


@bp.route('/create_group/<int:faculty_id>', methods=['GET', 'POST'])
def create_group(faculty_id):

    form = GroupForm()

    group = None

    if form.validate_on_submit():
        name = form.name.data
        subgroups = form.subgroups.data

        # Попробуйте найти существующую группу с заданным именем
        group = Group.query.filter_by(name=name).first()

        if group:
            # Если группа существует, обновите ее
            group.subgroups = subgroups
            flash('Group updated successfully', 'success')
        else:
            # Если группа не существует, создайте новую
            group = Group(name=name,
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

    if selected_group.subgroups is not None and selected_group.subgroups is not '':
        subgroups = [(0, 'Общее')] + [(int(subgroup), subgroup) for subgroup in selected_group.subgroups.split(',')]
    else:
        subgroups = [(0, 'Общее')]

    if form.validate_on_submit():
        group_name = selected_group.name
        subject_name = form.subject.data
        classroom_name = form.classroom.data
        day_of_week = form.day_of_week.data
        lesson_number = form.lesson_number.data
        weeks = form.weeks.data
        is_lecture = form.is_lecture.data

        # Получение существующих объектов группы, дисциплины и аудитории или их создание
        group = Group.query.filter_by(name=group_name).first()
        if not group:
            group = Group(name=group_name)
            db.session.add(group)
            db.session.commit()

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

        schedule_entry = Schedule(
            group_id=group.id,
            subgroup=selected_subgroup,
            subject_id=subject.id,
            classroom_id=classroom.id,
            day_of_week=day_of_week,
            lesson_number=lesson_number,
            weeks=','.join(weeks),  # сохраняем выбранные недели как строку
            is_lecture=is_lecture
        )

        db.session.add(schedule_entry)
        db.session.commit()

        return redirect(url_for('schedule.view_all_schedule'))

    return render_template('schedule/add_schedule.html',
                           form=form,
                           selected_group=selected_group,
                           groups=groups,
                           subjects=subjects,
                           classrooms=classrooms,
                           subgroups=subgroups,
                           selected_faculty=selected_faculty)


@bp.route('/view_all_schedule', methods=['GET'])
def view_all_schedule():
    schedule_entries = Schedule.query.all()

    # Проходим по всем записям и форматируем их недели
    for entry in schedule_entries:
        weeks_list = entry.weeks.split(',')
        formatted_weeks = []

        current_range = [int(weeks_list[0])]

        for week_str in weeks_list[1:]:
            week = int(week_str)
            if week == current_range[-1] + 1:
                current_range.append(week)
            else:
                if len(current_range) == 1:
                    formatted_weeks.append(str(current_range[0]))
                else:
                    formatted_weeks.append(f"{current_range[0]}-{current_range[-1]}")
                current_range = [week]

        if len(current_range) == 1:
            formatted_weeks.append(str(current_range[0]))
        else:
            formatted_weeks.append(f"{current_range[0]}-{current_range[-1]}")

        entry.weeks = ', '.join(formatted_weeks)

    return render_template('schedule/view_all_schedule.html',
                           schedule_entries=schedule_entries)


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

    selected_group_id = schedule_entry.group_id
    selected_group = Group.query.get(selected_group_id)
    selected_subgroup = schedule_entry.subgroup

    if not schedule_entry:
        flash('Schedule not found', 'danger')
        return redirect(url_for('view_all_schedule'))

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
    subgroups = [(0, 'Общее')] + [(int(subgroup), subgroup) for subgroup in selected_group.subgroups.split(',')]

    if form.validate_on_submit():
        group_name = selected_group.name
        subject_name = form.subject.data
        classroom_name = form.classroom.data
        day_of_week = form.day_of_week.data
        lesson_number = form.lesson_number.data
        weeks = form.weeks.data
        is_lecture = form.is_lecture.data

        # Получение существующих объектов группы, дисциплины и аудитории или их создание
        group = Group.query.filter_by(name=group_name).first()
        if not group:
            group = Group(name=group_name)
            db.session.add(group)
            db.session.commit()

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

        schedule_entry.group_id = group.id
        schedule_entry.subject_id = subject.id
        schedule_entry.classroom_id = classroom.id
        schedule_entry.day_of_week = day_of_week
        schedule_entry.lesson_number = lesson_number
        schedule_entry.weeks = ','.join(weeks)
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
                           selected_subgroup=selected_subgroup)
