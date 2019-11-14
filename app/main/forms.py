from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class SessionForm(FlaskForm):
    length_of_session = IntegerField('Length of Session (minutes)', validators=[DataRequired()])
    number_of_categories = IntegerField('# of Categories', validators=[DataRequired()])
    submit = SubmitField('Generate Session')

class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category_id = SelectField(u'Category', coerce=int)
    add_task_submit = SubmitField('Add Task')

    def __repr__(self):
        return f'<AddTaskForm: title={self.title,}>, description={self.description}, category_id={self.category_id}'


class AddCategoryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    add_category_submit = SubmitField('Add Category')

    def __repr__(self):
        return f'<AddCategoryForm: title={self.title,}>, description={self.description}'


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