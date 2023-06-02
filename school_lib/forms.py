from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import  IntegerField, StringField, PasswordField, SubmitField, RadioField, SelectField, validators
from wtforms.validators import DataRequired, Email


# when passed as a parameter to a template, an object of this class will be rendered as a regular HTML form
# with the additional restrictions specified for each field
# however forms are not used for every route

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    school_name = SelectField('School', validators=[DataRequired()])
    date_of_birth_day = SelectField('Day', validators=[DataRequired()])
    date_of_birth_month = SelectField('Month', validators=[DataRequired()])
    date_of_birth_year = SelectField('Year', validators=[DataRequired()])
    is_teacher = RadioField('Role', choices=[('Teacher'), ('Student')], validators=[DataRequired()])
    submit = SubmitField('Register')

class OperatorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    school_name = SelectField('School', validators=[DataRequired()])
    submit = SubmitField('Register')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[validators.DataRequired()])
    new_password = PasswordField('New Password', validators=[
        validators.DataRequired(),
        validators.Length(min=8, message='Password must be at least 8 characters long'),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[validators.DataRequired()])
    submit = SubmitField('Change Password')

class AddSchoolForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    street = StringField('Street', validators=[validators.DataRequired()])
    street_number = StringField('Street Number', validators=[validators.DataRequired()])
    postal_code = StringField('Postal Code', validators=[validators.DataRequired()])
    city = StringField('City', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired()])
    phone = StringField('Phone', validators=[validators.DataRequired()])
    principal_full_name = StringField('Principal Full Name', validators=[validators.DataRequired()])
    operator = SelectField('Operator', choices=[('', 'None')], validators=[validators.DataRequired()])
    submit = SubmitField('Add School')


class UpdateSchoolForm(FlaskForm):
    name = StringField('Name', render_kw={'readonly': True})
    street = StringField('Street', validators=[validators.DataRequired()])
    street_number = StringField('Street Number', validators=[validators.DataRequired()])
    postal_code = StringField('Postal Code', validators=[validators.DataRequired()])
    city = StringField('City', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired()])
    phone = StringField('Phone', validators=[validators.DataRequired()])
    principal_full_name = StringField('Principal Full Name', validators=[validators.DataRequired()])
    operator = SelectField('Operator', choices=[('', 'None')], validators=[validators.DataRequired()])
    submit = SubmitField('Update School')


class BookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    pages = IntegerField('Number of Pages', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired()])
    language = StringField('Language', default='Greek')
    summary = StringField('Summary')
    image = FileField('Book Image', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    available_copies = IntegerField('Available Copies', validators=[DataRequired()])

