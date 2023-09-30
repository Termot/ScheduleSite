from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import _
from flask_login import login_required
from app import db
from app.models import Schedule, Group, Subject, Classroom
from app.schedule import bp
from app.schedule.forms import ScheduleForm


@bp.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    form = ScheduleForm()

    # Подгружаем существующие значения для групп, дисциплин и аудиторий
    groups = [group for group in Group.query.all()]
    subjects = [subject for subject in Subject.query.all()]
    classrooms = [classroom for classroom in Classroom.query.all()]

    if form.validate_on_submit():
        group_name = form.group.data
        subject_name = form.subject.data
        classroom_name = form.classroom.data
        day_of_week = form.day_of_week.data
        weeks = form.weeks.data
        lesson_number = form.lesson_number.data

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
            group_id=group.id,
            subject_id=subject.id,
            classroom_id=classroom.id,
            day_of_week=day_of_week,
            weeks=', '.join(weeks),  # сохраняем выбранные недели как строку
            lesson_number=lesson_number
        )

        db.session.add(schedule_entry)
        db.session.commit()

        return redirect(url_for('schedule.view_all_schedule'))

    return render_template('schedule/add_schedule.html', form=form,
                           groups=groups,
                           subjects=subjects,
                           classrooms=classrooms)


@bp.route('/view_all_schedule', methods=['GET'])
def view_all_schedule():
    schedule_entries = Schedule.query.all()

    return render_template('schedule/view_all_schedule.html', schedule_entries=schedule_entries)
