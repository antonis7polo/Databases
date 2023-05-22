from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import TextAreaField,SelectMultipleField, IntegerField, StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField, validators
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.utils import secure_filename
import subprocess



## __name__ is the name of the module. When running directly from python, it will be 'school_lib'
## Outside of this module, as in run.py, it is '__main__' by default

## Create an instance of the Flask class to be used for request routing
app = Flask(__name__)

app.config['SECRET_KEY'] = 'dblab21'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = 'El20022!'
app.config["MYSQL_DB"] = 'School_Library'
app.config["MYSQL_HOST"] = 'localhost'

connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='El20022!',
        database='School_Library'
)

cursor = connection.cursor()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('Όνομα', validators=[DataRequired()])
    last_name = StringField('Επώνυμο', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    school_name = SelectField('Σχολείο', validators=[DataRequired()])
    date_of_birth_day = SelectField('Ημέρα', validators=[DataRequired()])
    date_of_birth_month = SelectField('Μήνας', validators=[DataRequired()])
    date_of_birth_year = SelectField('Έτος', validators=[DataRequired()])
    is_teacher = RadioField('Ιδιότητα', choices=[('Καθηγητής'), ('Μαθητής')], validators=[DataRequired()])
    submit = SubmitField('Εγγραφή')

class OperatorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('Όνομα', validators=[DataRequired()])
    last_name = StringField('Επώνυμο', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    school_name = SelectField('Σχολείο', validators=[DataRequired()])
    submit = SubmitField('Εγγραφή')

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
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    phone = StringField('Phone', validators=[validators.DataRequired()])
    principal_full_name = StringField('Principal Full Name', validators=[validators.DataRequired()])
    operator = SelectField('Operator', choices=[('', 'None')], validators=[validators.DataRequired()])
    submit = SubmitField('Add School')

class BookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    pages = IntegerField('Number of Pages', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired()])
    language = StringField('Language', default='Greek')
    summary = StringField('Summary')
    image_url = StringField('Image URL')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register/user', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form.school_name.choices = get_schools_from_database()  # Populate the dropdown list with schools from the database
    form.date_of_birth_day.choices = [(str(i), str(i)) for i in range(1, 32)]
    form.date_of_birth_month.choices = [(str(i), str(i)) for i in range(1, 13)]
    form.date_of_birth_year.choices = [(str(i), str(i)) for i in range(1940, 2023)]
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        school_name = form.school_name.data
        date_of_birth_day = int(form.date_of_birth_day.data)
        date_of_birth_month = int(form.date_of_birth_month.data)
        date_of_birth_year = int(form.date_of_birth_year.data)
        date_of_birth = f'{date_of_birth_year}-{date_of_birth_month:02d}-{date_of_birth_day:02d}'
        is_teacher = form.is_teacher.data == 'Καθηγητής'

        cursor.execute("INSERT INTO Pending_Registrations (Username, Password, First_Name, Last_Name, Email, School_Name, Date_Of_Birth, Is_Teacher) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (username, password, first_name, last_name, email, school_name, date_of_birth, is_teacher))
        connection.commit()

        return 'Registration request successful. Soon you will be able to access the library if everything is OK'
    return render_template('register.html', form=form)

@app.route('/register/operator', methods=['GET', 'POST'])
def operator_register():
    form = OperatorRegistrationForm()
    form.school_name.choices = get_schools_from_database()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        school_name = form.school_name.data

        cursor.execute("""
            INSERT INTO Operator_Registration (Username, Password, First_Name, Last_Name, Email, School_Name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password, first_name, last_name, email, school_name))
        connection.commit()

        return 'Registration request successful. Soon you will be able to access the library, if everything is OK'
    return render_template('operator_register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user is an operator
        cursor.execute("SELECT Operator_ID FROM Operator WHERE Username = %s AND Password = %s", (username, password))
        operator = cursor.fetchone()
        if operator:
            operator_id = operator[0]
            session['id'] = operator_id
            session['username'] = username  # Store the username in the session
            return redirect(url_for('operator'))

        # Check if the user is an administrator
        cursor.execute("SELECT Administrator_ID FROM Administrator WHERE Username = %s AND Password = %s", (username, password))
        administrator = cursor.fetchone()
        if administrator:
            administrator_id = administrator[0]
            session['id'] = administrator_id
            session['username'] = username  # Store the username in the session
            return redirect(url_for('administrator'))

        # Check if the user is a teacher
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s AND Password = %s AND Is_Teacher = True", (username, password))
        teacher = cursor.fetchone()
        if teacher:
            user_id = teacher[0]  # Get the User_ID from the fetched row
            session['id'] = user_id  # Store the ID in the session
            session['username'] = username  # Store the username in the session
            return redirect(url_for('teacher'))

        # Check if the user is a student
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s AND Password = %s AND Is_Teacher = False", (username, password))
        student = cursor.fetchone()
        if student:
            user_id = student[0]  # Get the User_ID from the fetched row
            session['id'] = user_id  # Store the ID in the session
            session['username'] = username  # Store the username in the session
            return redirect(url_for('student'))

        # If no user is found, display an error message
        error_message = 'Wrong username or password, try again'
    
    return render_template('home.html', error_message=error_message)

@app.route('/operator')
def operator():
    username = session.get('username')
    return render_template('operator.html',username=username)

@app.route('/administrator')
def administrator():
    username = session.get('username')
    return render_template('administrator.html',username=username)

@app.route('/teacher')
def teacher():
    username = session.get('username')
    return render_template('teacher.html',username=username)

@app.route('/student')
def student():
    username = session.get('username')
    return render_template('student.html',username=username)

@app.route('/change_password/operator', methods=['GET', 'POST'])
def change_operator_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Retrieve user input from the form
        current_password = form.current_password.data
        new_password = form.new_password.data

        operator_id = session.get('id')  
        # Check if the current password matches the one stored in the database
        cursor.execute("SELECT Password FROM Operator WHERE Operator_ID = %s", (operator_id,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            print(current_password)
            print(stored_password)
            if current_password == stored_password:
                # Update the password in the database
                cursor.execute("UPDATE Operator SET Password = %s WHERE Operator_ID = %s", (new_password, operator_id))
                connection.commit()

                return 'Password changed successfully'

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message)

    return render_template('change_password.html', form=form, user_type = 'operator')

@app.route('/change_password/user', methods=['GET', 'POST'])
def change_user_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Retrieve user input from the form
        current_password = form.current_password.data
        new_password = form.new_password.data

        user_id = session.get('id')  

        # Check if the current password matches the one stored in the database
        cursor.execute("SELECT Password FROM User WHERE User_ID = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]

            if current_password == stored_password:
                # Update the password in the database
                cursor.execute("UPDATE User SET Password = %s WHERE User_ID = %s", (new_password, user_id))
                connection.commit()

                return 'Password changed successfully'

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message)

    return render_template('change_password.html', form=form, user_type = 'user')


@app.route('/change_password/administrator', methods=['GET', 'POST'])
def change_admin_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Retrieve user input from the form
        current_password = form.current_password.data
        new_password = form.new_password.data

        admin_id = session.get('id')  

        # Check if the current password matches the one stored in the database
        cursor.execute("SELECT Password FROM Administrator WHERE Administrator_ID = %s", (admin_id,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]

            if current_password == stored_password:
                # Update the password in the database
                cursor.execute("UPDATE Administrator SET Password = %s WHERE Administrator_ID = %s", (new_password, admin_id))
                connection.commit()

                return 'Password changed successfully'

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message)

    return render_template('change_password.html', form=form, user_type = 'administrator')

@app.route('/backup_database', methods=['POST'])
def backup_database():
    # Retrieve the necessary information for the database backup
    db_host = 'localhost'
    db_user = 'root'
    db_password = 'El20022!'
    db_name = 'School_Library'
    backup_dir = request.form.get('backup_dir')


    # Generate the backup file name (e.g., database_backup.sql)
    backup_filename = 'database_backup.sql'

    # Construct the full backup path
    backup_path = f"{backup_dir}/{backup_filename}"

    # Construct the command to perform the database backup using mysqldump
    command = f"mysqldump -h {db_host} -u {db_user} -p{db_password} {db_name} > {backup_path}"

    try:
        # Execute the command to create the database backup
        subprocess.run(command, shell=True, check=True)
        return 'Database backup created successfully'
    except subprocess.CalledProcessError as e:
        # An error occurred during the backup process
        error_message = f"Database backup failed: {e}"
        return error_message


@app.route('/restore_database', methods=['POST'])
def restore_database():
    # Retrieve the necessary information for database restoration
    db_host = 'localhost'
    db_user = 'root'
    db_password = 'El20022!'
    db_name = 'foo'

    # Check if a file was uploaded
    if 'restore_file' not in request.files:
        return 'No file uploaded'

    # Get the uploaded file
    restore_file = request.files['restore_file']

    # Check if the file name is empty
    if restore_file.filename == '':
        return 'No file selected'

    # Save the uploaded file with a secure filename
    filename = secure_filename(restore_file.filename)
    restore_file.save(filename)

    # Construct the command to restore the database using mysql
    command = f"mysql -h {db_host} -u {db_user} -p{db_password} {db_name} < {filename}"

    try:
        # Execute the command to restore the database
        subprocess.run(command, shell=True, check=True)
        return 'Database restored successfully'
    except subprocess.CalledProcessError as e:
        # An error occurred during the restoration process
        error_message = f"Database restoration failed: {e}"
        return error_message

@app.route('/school/add_school', methods=['GET', 'POST'])
def add_school():
    form = AddSchoolForm()
    print(form.operator.data)

    query = "SELECT Operator_ID, First_Name, Last_Name FROM Operator"
    cursor.execute(query)
    operators = cursor.fetchall()
    operator_choices = [(0, 'None')] + [(operator[0], f"{operator[0]} - {operator[1]} {operator[2]}") for operator in operators]
    form.operator.choices = operator_choices

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        street = form.street.data
        street_number = int(form.street_number.data)
        postal_code = form.postal_code.data
        city = form.city.data
        email = form.email.data
        phone = form.phone.data
        principal_full_name = form.principal_full_name.data
        operator_id = int(form.operator.data) 
        if operator_id > 0:
            query = "INSERT INTO School (Name, Street, Street_Number, Postal_Code, City, Email, Phone, Principal_Full_Name, Operator_ID) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        else:
            query = "INSERT INTO School (Name, Street, Street_Number, Postal_Code, City, Email, Phone, Principal_Full_Name) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, street, street_number, postal_code, city, email, phone, principal_full_name)
        cursor.execute(query, values)
        connection.commit()
        return 'School added successfully!'

    return render_template('add_school.html', form=form)

@app.route('/operator_management', methods=['GET', 'POST'])
def operator_management():
    operator_query = "SELECT o.Operator_ID, o.Username, o.First_Name, o.Last_Name, o.Email, s.Name  FROM Operator o INNER JOIN School s ON o.Operator_ID = s.Operator_ID"
    registration_query = "SELECT Operator_ID, Username, First_Name, Last_Name, Email, School_Name FROM Operator_Registration"
    cursor.execute(operator_query)
    operators = cursor.fetchall()
    cursor.execute(registration_query)
    registrations = cursor.fetchall()

    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            operator_username = request.form['operator_username']
            accept_registration_procedure = "CALL accept_operator_registrations(%s)"
            cursor.execute(accept_registration_procedure, (operator_username,))
            connection.commit()
            return 'Operator added successfully!'

        elif action == 'decline':
            operator_username = request.form['operator_username']
            decline_registration_query = "DELETE FROM Operator_Registration WHERE Username = %s"
            cursor.execute(decline_registration_query, (operator_username,))
            connection.commit()
            return 'Operator registration declined'
        
        elif action == 'delete':
            operator_id = request.form['operator_id']
            delete_operator_procedure = "CALL delete_operator(%s)"
            cursor.execute(delete_operator_procedure, (operator_id,))
            connection.commit()
            return 'Operator deleted successfully!'

    return render_template('operator_management.html', operators=operators, registrations=registrations)

@app.route('/books')
def books():
    cursor.execute("SELECT b.ISBN, b.Title, b.Number_Of_Pages, b.Publisher, b.Language, b.Summary, b.Image_URL, "
                "GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name)) AS Authors, "
                "GROUP_CONCAT(DISTINCT k.Keyword) AS Keywords, "
                "GROUP_CONCAT(DISTINCT c.Genre) AS Categories "
                "FROM Book b "
                "LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN "
                "LEFT JOIN Author a ON ba.Author_ID = a.Author_ID "
                "LEFT JOIN Book_Keyword bk ON b.ISBN = bk.ISBN "
                "LEFT JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID "
                "LEFT JOIN Book_Category bc ON b.ISBN = bc.ISBN "
                "LEFT JOIN Category c ON bc.Category_Id = c.Category_Id "
                "GROUP BY b.ISBN")

    books_data = cursor.fetchall()

    return render_template('books.html', books=books_data)



def get_schools_from_database():
    cursor.execute("SELECT Name FROM School")
    schools = cursor.fetchall()
    return [(school[0], school[0]) for school in schools]

@app.route('/school', methods=['GET'])
def schools():
    # Query to fetch all schools from the database
    query = "SELECT Name, Street, Street_Number, Postal_Code, City, Email, Phone, Principal_Full_Name, Operator_ID FROM School"
    cursor.execute(query)
    schools = cursor.fetchall()

    return render_template('school.html', schools=schools)




if __name__ == '__main__':
    app.run(debug=True)