from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

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