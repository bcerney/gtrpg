from flask_wtf import FlaskForm
from wtforms import (HiddenField, SelectField,
                     SelectMultipleField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

from app.models import User


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class NewSessionAddTaskForm(FlaskForm):
    task_id = SelectField(u'Task', coerce=int)
    new_session_add_task_submit = SubmitField('Add Task')


class RunSessionForm(FlaskForm):
    session_id = HiddenField()
    # session_tasks = MultiCheckboxField("Session Tasks", coerce=int)
    run_session_submit = SubmitField('Finish Session')


# class SessionForm(FlaskForm):
#     length_of_session = IntegerField('Length of Session (minutes)', validators=[DataRequired()])
#     number_of_categories = IntegerField('# of Categories', validators=[DataRequired()])
#     submit = SubmitField('Generate Session')


class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    xp = SelectField(u'XP', choices=[(1, '1'), (2, '2'), (3, '3'), (5, '5'), (8, '8'), (13, '13')], coerce=int)
    category_id = SelectField(u'Category', coerce=int)
    add_task_submit = SubmitField('Add Task')

    def __repr__(self):
        return f'<AddTaskForm: title={self.title,}>, description={self.description}, xp={self.xp}, category_id={self.category_id}'


class AddCategoryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    add_category_submit = SubmitField('Add Category')

    def __repr__(self):
        return f'<AddCategoryForm: title={self.title,}>, description={self.description}'


class AddUserCategoryForm(FlaskForm):
    category_id = SelectField(u'Category', coerce=int)
    add_user_category_submit = SubmitField('Add Category')

    def __repr__(self):
        return f'<AddUserCategoryForm: category_id={self.category_id}'


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
