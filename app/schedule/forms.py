from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField, StringField, IntegerField
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput

DAY_OF_WEEK_CHOICES = [(day, day) for day in
                       ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']]
WEEKS_CHOICES = [(f'{i}', f'{i}') for i in range(1, 20)]


class ScheduleForm(FlaskForm):
    group = StringField('Group', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    classroom = StringField('Classroom', validators=[DataRequired()])
    day_of_week = SelectField('Day of Week',
                              choices=DAY_OF_WEEK_CHOICES,
                              validators=[DataRequired()])
    weeks = SelectMultipleField('Weeks',
                                choices=WEEKS_CHOICES,
                                validators=[DataRequired()],
                                widget=ListWidget(prefix_label=False),
                                option_widget=CheckboxInput())
    lesson_number = IntegerField('Lesson Number', validators=[DataRequired()])
