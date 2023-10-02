import json

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import _
from flask_login import login_required
from app import db
from app.models import Schedule, Group, Subject, Classroom
from app.schedule import bp
from app.schedule.forms import ScheduleForm, GroupForm


@bp.route('/', methods=['GET', 'POST'])
def main():
    groups = [group for group in Group.query.all()]

    return render_template('schedule/main.html',
                           groups=groups)


@bp.route('/create_group', methods=['GET', 'POST'])
def create_group():
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
            group = Group(name=name, subgroups=subgroups)
            db.session.add(group)
            flash('Group created successfully', 'success')

        db.session.commit()

        return redirect(url_for('schedule.main'))

    return render_template('schedule/create_group.html',
                           form=form,
                           group=group)


@bp.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    selected_group_id = request.args.get('selected_group')
    selected_group = Group.query.get(selected_group_id)

    form = ScheduleForm()
    form.group.data = selected_group

    if selected_group is None:
        flash('Group not found', 'danger')
        return redirect(url_for('view_all_groups'))

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
                           subgroups=subgroups)


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


@bp.route('/delete_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def delete_schedule(schedule_id):
    schedule_entry = Schedule.query.get(schedule_id)

    if not schedule_entry:
        flash('Schedule not found', 'danger')
        return redirect(url_for('view_all_schedule'))

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
