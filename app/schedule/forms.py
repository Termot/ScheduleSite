from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, \
    IntegerField, BooleanField, FieldList, SubmitField
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import DataRequired, NumberRange

DAY_OF_WEEK_CHOICES = [(day, day) for day in
                       ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']]
WEEKS_CHOICES = [(f'{i}', f'{i}') for i in range(1, 20)]


class FacultyForm(FlaskForm):
    name = StringField('Faculty Name', validators=[DataRequired()])
    submit = SubmitField('Create Faculty')


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    full_name = StringField('Group Full Name', validators=[DataRequired()])
    subgroups = StringField('Subgroup')


class ScheduleForm(FlaskForm):
    faculty = StringField('Faculty', validators=[DataRequired()])
    group = StringField('Group', validators=[DataRequired()])
    subgroup = FieldList(IntegerField('Subgroup', validators=[DataRequired()]))
    subject = StringField('Subject', validators=[DataRequired()])
    classroom = StringField('Classroom', validators=[DataRequired()])
    day_of_week = SelectField('Day of Week',
                              choices=DAY_OF_WEEK_CHOICES,
                              validators=[DataRequired()])
    lesson_number = IntegerField('Lesson Number',
                                 validators=[DataRequired(),
                                             NumberRange(min=1, max=8), ],
                                 default=1)
    weeks = SelectMultipleField('Weeks',
                                choices=WEEKS_CHOICES,
                                validators=[DataRequired()])
    even_weeks = FieldList(IntegerField('Evenness Weeks', validators=[DataRequired()]))
    is_lecture = BooleanField('Is Lecture')
