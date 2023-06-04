from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import subprocess
import mysql.connector
from urllib.parse import urlencode
from datetime import datetime
import os
from school_lib import app, connection # initially created by __init__.py, need to be used here
from school_lib.forms import *

cursor = connection.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user/register', methods=['GET', 'POST'])
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
        is_teacher = form.is_teacher.data == 'Teacher'

        try:
            cursor.execute("INSERT INTO Pending_Registrations (Username, Password, First_Name, Last_Name, Email, School_Name, Date_Of_Birth, Is_Teacher) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (username, password, first_name, last_name, email, school_name, date_of_birth, is_teacher))
            connection.commit()
            message = 'Registration request successful. Soon you will be able to access the library if everything is OK'
            return render_template('home.html', message=message)
        except mysql.connector.Error as error:
            if error.errno == 1644:  # Duplicate entry error for unique fields
                if 'Username' in str(error):
                    form.username.errors.append('Username already in use.')
                if 'Email already' in str(error):
                    form.email.errors.append('Email already in use.')
                    return render_template('register.html', form=form, email_error=True)
                if 'Invalid' in str(error):
                    form.email.errors.append('Invalid email format.')
                    return render_template('register.html', form=form, email_format_error=True)
            else:
                flash('An error occurred while processing your request. Please try again later.', 'error')

    return render_template('register.html', form=form)

@app.route('/operator/register', methods=['GET', 'POST'])
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
        try:
            cursor.execute("""
                INSERT INTO Operator_Registration (Username, Password, First_Name, Last_Name, Email, School_Name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, password, first_name, last_name, email, school_name))
            connection.commit()

            message = 'Registration request successful. Soon you will be able to access the library if everything is OK'
            return render_template('home.html', message=message)    
        except mysql.connector.Error as error:
            if error.errno == 1644:  # Duplicate entry error for unique fields
                if 'Username' in str(error):
                    form.username.errors.append('Username already in use.')
                if 'Email already' in str(error):
                    form.email.errors.append('Email already in use.')
                    return render_template('operator_register.html', form=form, email_error=True)
                if 'Invalid' in str(error):
                    form.email.errors.append('Invalid email format.')
                    return render_template('operator_register.html', form=form, email_format_error=True)
            else:
                flash('An error occurred while processing your request. Please try again later.', 'error')

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
            session['role'] = 'operator'
            return redirect(url_for('operator'))

        # Check if the user is an administrator
        cursor.execute("SELECT Administrator_ID FROM Administrator WHERE Username = %s AND Password = %s", (username, password))
        administrator = cursor.fetchone()
        if administrator:
            administrator_id = administrator[0]
            session['id'] = administrator_id
            session['username'] = username  # Store the username in the session
            session['role'] = 'administrator'
            return redirect(url_for('administrator'))

        # Check if the user is a teacher
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s AND Password = %s AND Is_Teacher = True", (username, password))
        teacher = cursor.fetchone()
        if teacher:
            user_id = teacher[0]  # Get the User_ID from the fetched row
            session['id'] = user_id  # Store the ID in the session
            session['username'] = username  # Store the username in the session
            session['role'] = 'teacher'
            return redirect(url_for('teacher'))

        # Check if the user is a student
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s AND Password = %s AND Is_Teacher = False", (username, password))
        student = cursor.fetchone()
        if student:
            user_id = student[0]  # Get the User_ID from the fetched row
            session['id'] = user_id  # Store the ID in the session
            session['username'] = username  # Store the username in the session
            session['role'] = 'student'
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

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return render_template('home.html')

@app.route('/delete_account', methods=['POST'])
def delete_account():

    username = session.get('username')

    # Delete the user's account
    cursor.execute("DELETE FROM User WHERE Username = %s", (username,))
    connection.commit()

    # Clear the user's session
    session.clear()

    return redirect(url_for('home'))  

@app.route('/delete_account_page')
def delete_account_page():
    return render_template('delete_account.html')

@app.route('/student/profile')
def user_profile():
    # Ensure that the user is logged in before allowing them to see their profile
    if 'username' in session:
        username = session['username']
        
        # Fetch user details
        user_query = """
        SELECT Username, Password, First_Name, Last_Name, Email, School_Name, Date_Of_Birth
        FROM User 
        WHERE Username = %s
        """
        cursor.execute(user_query, (username,))
        user = cursor.fetchone()

        # If the user doesn't exist, return an error
        if not user:
            return "Error: User not found"

        # Pass the user details to the template
        return render_template('student_profile.html', user=user)

    else:
        # If the user is not logged in, redirect them to the login page
        return redirect(url_for('login')) 

   

@app.route('/operator/change_password', methods=['GET', 'POST'])
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
            if current_password == stored_password:
                # Update the password in the database
                cursor.execute("UPDATE Operator SET Password = %s WHERE Operator_ID = %s", (new_password, operator_id))
                connection.commit()
                message = 'Password changed successfully'
                return render_template('home.html', message = message)

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message, user_type = 'operator')

    return render_template('change_password.html', form=form, user_type = 'operator')

@app.route('/user/change_password', methods=['GET', 'POST'])
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
                message = 'Password changed successfully'
                return render_template('home.html', message = message)

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message, user_type = 'user')

    return render_template('change_password.html', form=form, user_type = 'user')


@app.route('/administrator/change_password', methods=['GET', 'POST'])
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

                message = 'Password changed successfully'
                return render_template('home.html', message = message)

        # If the current password is incorrect or user not found, display an error message
        error_message = 'Invalid current password'
        return render_template('change_password.html', form=form, error_message=error_message, user_type = 'administrator')

    return render_template('change_password.html', form=form, user_type = 'administrator')

@app.route('/administrator/backup_database', methods=['POST'])
def backup_database():
    # Retrieve the necessary information for the database backup
    username = session.get('username')
    db_host = 'localhost'
    db_user = 'root'
    db_name = 'School_Library_New'
    backup_dir = request.form.get('backup_dir')


    backup_filename = 'database_backup.sql'

    # Construct the full backup path
    backup_path = f"{backup_dir}/{backup_filename}"

    # Construct the command to perform the database backup using mysqldump
    command = f"mysqldump -h {db_host} -u {db_user} -p  {db_name} > {backup_path}"

    try:
        # Execute the command to create the database backup
        subprocess.run(command, shell=True, check=True)
        message = 'Backup created succesfully!'
        return render_template('administrator.html', username = username, message = message)
    except subprocess.CalledProcessError as e:
        # An error occurred during the backup process
        error_message = f"Database backup failed: {e}"
        return error_message


@app.route('/administrator/restore_database', methods=['POST'])
def restore_database():
    username = session.get('username')
    # Retrieve the necessary information for database restoration
    db_host = 'localhost'
    db_user = 'root'
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
    command = f"mysql -h {db_host} -u {db_user} -p {db_name} < {filename}"

    try:
        # Execute the command to restore the database
        subprocess.run(command, shell=True, check=True)
        message = 'Database restored successfully'
        return render_template('administrator.html', username = username, message = message)
    except subprocess.CalledProcessError as e:
        # An error occurred during the restoration process
        error_message = f"Database restoration failed: {e}"
        return error_message

def get_schools_from_database():
    cursor.execute("SELECT Name FROM School")
    schools = cursor.fetchall()
    return [(school[0], school[0]) for school in schools]

@app.route('/administrator/school', methods=['GET'])
def schools():
    message = request.args.get('message')
    # Query to fetch all schools from the database
    query = "SELECT s.Name, s.Street, s.Street_Number, s.Postal_Code, s.City, s.Email, s.Phone, s.Principal_Full_Name, CONCAT(o.First_Name, ' ', o.Last_Name) as  Operator_Name FROM School s LEFT JOIN Operator o ON s.Operator_ID = o.Operator_ID"
    cursor.execute(query)
    schools = cursor.fetchall()

    return render_template('school.html', schools=schools,message = message)


@app.route('/administrator/school/add_school', methods=['GET', 'POST'])
def add_school():
    form = AddSchoolForm()
    username = session.get('username')
    query = "SELECT Operator_ID, First_Name, Last_Name FROM Operator"
    cursor.execute(query)
    operators = cursor.fetchall()
    operator_choices = [(0, 'None')] + [(operator[0], f"{operator[0]} - {operator[1]} {operator[2]}") for operator in operators]
    form.operator.choices = operator_choices

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        street = form.street.data
        street_number = form.street_number.data
        postal_code = form.postal_code.data
        city = form.city.data
        email = form.email.data
        phone = form.phone.data
        principal_full_name = form.principal_full_name.data
        operator_id = int(form.operator.data)

        if operator_id > 0:
            query = "INSERT INTO School (Name, Street, Street_Number, Postal_Code, City, Email, Phone, Principal_Full_Name, Operator_ID) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (name, street, street_number, postal_code, city, email, phone, principal_full_name, operator_id)

        else:
            query = "INSERT INTO School (Name, Street, Street_Number, Postal_Code, City, Email, Phone, Principal_Full_Name) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (name, street, street_number, postal_code, city, email, phone, principal_full_name)

        try:
            cursor.execute(query, values)
            connection.commit()
            message = 'School added successfully!'
            return render_template('administrator.html', username=username, message=message)
        except mysql.connector.Error as error:
            if error.errno == 1644:
                error_message = error.msg
            elif error.errno == 1062:
                error_message = 'A School with this name already exists.'
            else:
                error_message = 'An error occurred while adding the school. Check all fields'

            return render_template('add_school.html', form=form, error_message=error_message)

    return render_template('add_school.html', form=form)


@app.route('/administrator/school/update_school/<name>', methods=['GET', 'POST'])
def update_school(name):
    username = session.get('username')
    form = UpdateSchoolForm()
    query = "SELECT Operator_ID, First_Name, Last_Name FROM Operator"
    cursor.execute(query)
    operators = cursor.fetchall()
    operator_choices = [(0, 'None')] + [(operator[0], f"{operator[0]} - {operator[1]} {operator[2]}") for operator in operators]
    form.operator.choices = operator_choices

    # Retrieve the existing school details from the database
    cursor.execute("SELECT * FROM School WHERE Name = %s", (name,))
    school = cursor.fetchone()

    if school:
        # Populate the form with the existing school details
        form.name.data = school[0]
        form.street.data = school[1]
        form.street_number.data = school[2]
        form.postal_code.data = school[3]
        form.city.data = school[4]
        form.email.data = school[5]
        form.phone.data = school[6]
        form.principal_full_name.data = school[7]
        form.operator.data = school[8]

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
            query = "UPDATE School SET Street = %s, Street_Number = %s, Postal_Code = %s, City = %s, " \
                    "Email = %s, Phone = %s, Principal_Full_Name = %s, Operator_ID = %s WHERE Name = %s"
            values = (street, street_number, postal_code, city, email, phone, principal_full_name, operator_id, name)
        else:
            query = "UPDATE School SET Street = %s, Street_Number = %s, Postal_Code = %s, City = %s, " \
                    "Email = %s, Phone = %s, Principal_Full_Name = %s, Operator_ID = NULL WHERE Name = %s"
            values = (street, street_number, postal_code, city, email, phone, principal_full_name, name)
        try:
            cursor.execute(query, values)
            connection.commit()
            message = 'School updated successfully!'
            return render_template('administrator.html', username=username, message=message)
        except mysql.connector.Error as error:
            if error.errno == 1644:
                error_message = error.msg
            else:
                error_message = 'Invalid Postal Code'
      
            return render_template('update_school.html', form=form, school=name, error_message = error_message)

    return render_template('update_school.html', form=form, school=name)


@app.route('/administrator/school/delete_school/<name>', methods=['GET'])
def delete_school(name):
    username = session.get('username')
    # Delete all users of the school
    cursor.execute("DELETE FROM User WHERE School_Name = %s", (name,))
    connection.commit()

    # Delete the school itself
    cursor.execute("DELETE FROM School WHERE Name = %s", (name,))
    connection.commit()

    message = 'School deleted successfully!'
    return render_template('administrator.html', username = username, message = message)


@app.route('/administrator/operator_management', methods=['GET', 'POST'])
def operator_management():
    username = session.get('username')
    operator_query = "SELECT o.Operator_ID, o.Username, o.First_Name, o.Last_Name, o.Email, s.Name  FROM Operator o LEFT JOIN School s ON o.Operator_ID = s.Operator_ID"
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
            message = 'Operator added successfully!'
            return render_template('administrator.html', username = username, message = message)

        elif action == 'decline':
            operator_username = request.form['operator_username']
            decline_registration_query = "DELETE FROM Operator_Registration WHERE Username = %s"
            cursor.execute(decline_registration_query, (operator_username,))
            connection.commit()
            message = 'Operator registration declined'
            return render_template('administrator.html', username = username, message = message)

        
        elif action == 'delete':
            operator_id = request.form['operator_id']
            delete_operator_procedure = "CALL delete_operator(%s)"
            cursor.execute(delete_operator_procedure, (operator_id,))
            connection.commit()
            message = 'Operator deleted successfully!'
            return render_template('administrator.html', username = username, message = message)


    return render_template('operator_management.html', operators=operators, registrations=registrations)


@app.route('/operator/books', methods=['GET', 'POST'])
def books():
    search_query = request.args.get('search')
    username = session.get('username')
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query, (username,))
    school_name = cursor.fetchone()

    if search_query:
        # Handle the search query
        cursor.execute("SELECT b.ISBN, b.Title, b.Number_Of_Pages, b.Publisher, b.Language, b.Summary, b.Image_URL, "
                       "GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name, ' (ID: ', a.Author_ID, ')')) AS Authors, "
                       "GROUP_CONCAT(DISTINCT k.Keyword) AS Keywords, "
                       "GROUP_CONCAT(DISTINCT c.Genre) AS Categories, "
                       "(SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = %s) as Available_Copies "
                       "FROM Book b "
                       "INNER JOIN School_Books sb ON b.ISBN = sb.ISBN "
                       "INNER JOIN Book_Author ba ON b.ISBN = ba.ISBN "
                       "INNER JOIN Author a ON ba.Author_ID = a.Author_ID "
                       "INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN "
                       "INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID "
                       "INNER JOIN Book_Category bc ON b.ISBN = bc.ISBN "
                       "INNER JOIN Category c ON bc.Category_Id = c.Category_Id "
                       "WHERE b.Title LIKE CONCAT('%', %s, '%') "
                       "AND sb.School_Name = %s "
                       "GROUP BY b.ISBN", (school_name[0], search_query, school_name[0]))
        books_data = cursor.fetchall()
    else:
        # Fetch all books
        cursor.execute("SELECT b.ISBN, b.Title, b.Number_Of_Pages, b.Publisher, b.Language, b.Summary, b.Image_URL, "
                       "GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name, ' (ID: ', a.Author_ID, ')')) AS Authors, "
                       "GROUP_CONCAT(DISTINCT k.Keyword) AS Keywords, "
                       "GROUP_CONCAT(DISTINCT c.Genre) AS Categories, "
                       "(SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = %s) as Available_Copies "
                       "FROM Book b "
                       "INNER JOIN School_Books sb ON b.ISBN = sb.ISBN "
                       "INNER JOIN Book_Author ba ON b.ISBN = ba.ISBN "
                       "INNER JOIN Author a ON ba.Author_ID = a.Author_ID "
                       "INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN "
                       "INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID "
                       "INNER JOIN Book_Category bc ON b.ISBN = bc.ISBN "
                       "INNER JOIN Category c ON bc.Category_Id = c.Category_Id "
                       "WHERE sb.School_Name = %s "
                       "GROUP BY b.ISBN", (school_name[0],school_name[0]))
        books_data = cursor.fetchall()


    message = request.args.get("message")
    return render_template('books.html', books=books_data, message=message)


@app.route('/operator/books/delete_book/<isbn>', methods=['GET'])
def delete_book(isbn):
    username = session.get('username')
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query, (username,))
    school_name = cursor.fetchone()

    # Delete the book from the school_books table
    cursor.execute("DELETE FROM School_Books WHERE School_Name = %s AND ISBN = %s", (school_name[0], isbn))
    connection.commit()

    message = 'Book deleted successfully!'
    query_params = urlencode({"message": message})
    redirect_url = f"/operator/books?{query_params}"
    return redirect(redirect_url)


@app.route('/operator/books/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    username = session.get('username')
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query,(username,))
    school_name = cursor.fetchone()

    if form.validate_on_submit():
        try:
            isbn = form.isbn.data
            title = form.title.data
            num_pages = form.pages.data
            publisher = form.publisher.data
            language = form.language.data
            summary = form.summary.data
            image_file = form.image.data  # get the FileStorage instance
            authors = request.form.getlist('authors')
            categories = request.form.getlist('categories')  # Get the selected categories from the form
            keywords = request.form.getlist('keywords') # Get the selected keywords from the form
            available_copies = form.available_copies.data
            filename = secure_filename(image_file.filename)  # get the secure filename
            image_file.save(os.path.join('school_lib/static/images', filename))  # save the file
            book_query = "SELECT * FROM Book WHERE ISBN = %s"
            cursor.execute(book_query, (isbn,))
            book_result = cursor.fetchone()
        except AttributeError as error:
            error_message = 'An error occurred. Check if all fields are correct.'
            return render_template('add_book.html', form=form, error_message= error_message)   

        if not book_result:
            # The book doesn't exist, so insert it into the book table
            try:
                cursor.execute("INSERT INTO Book (ISBN, Title, Number_Of_Pages, Publisher, Language, Summary, Image_URL) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (isbn, title, num_pages, publisher, language, summary, 'images/' + filename))
            except mysql.connector.Error as error:
                error_message = 'An error occurred. Check if all fields are correct.'
                return render_template('add_book.html', form=form, error_message= error_message)   

            # Insert the book authors into the Book_Author table
            authors = [author.strip() for author in ','.join(authors).split(',')]
            for author in authors:
                if ':' in author:
                    author_info = author.split(':')
                    if len(author_info) == 2:
                        author_id = author_info[0].strip()
                        first_name, last_name = [name.strip() for name in author_info[1].split()]

                    else:
                        continue
                else:
                    first_name, last_name = [name.strip() for name in author.split()]
                    author_id = None

                if author_id:
                    cursor.execute("SELECT Author_ID FROM Author WHERE Author_ID = %s", (author_id,))
                    author_data = cursor.fetchone()
                else:
                    try:
                        cursor.execute("SELECT Author_ID FROM Author WHERE First_Name = %s AND Last_Name = %s",
                                    (first_name, last_name))
                        author_data = cursor.fetchone()
                        if cursor.fetchone() is not None:
                            error_message = 'There are multiple authors with the same full name. Please provide the author ID.'
                            return render_template('add_book.html', form=form, error_message=error_message)
                    except mysql.connector.errors.InternalError as error:
                        error_message = 'An error occurred while fetching author data.'
                        return render_template('add_book.html', form=form, error_message = error_message) 
                      
                if author_data:
                    author_id = author_data[0]
                else:
                    cursor.execute("INSERT INTO Author (First_Name, Last_Name) VALUES (%s, %s)", (first_name, last_name))
                    author_id = cursor.lastrowid

                cursor.execute("INSERT INTO Book_Author (Author_ID, ISBN) VALUES (%s, %s)", (author_id, isbn))


            categories = [category.strip() for category in ','.join(categories).split(',')]
            #Insert the book categories into the Book_Category table
            for category in categories:
                cursor.execute("SELECT Category_Id FROM Category WHERE Genre = %s", (category,))
                category_data = cursor.fetchone()
                if category_data:
                    category_id = category_data[0]
                else:
                    cursor.execute("INSERT INTO Category (Genre) VALUES (%s)", (category,))
                    category_id = cursor.lastrowid

                cursor.execute("INSERT INTO Book_Category (Category_Id, ISBN) VALUES (%s, %s)", (category_id, isbn))
        
            keywords = [keyword.strip() for keyword in ','.join(keywords).split(',')]
            # Insert the book keywords into the Book_Keyword table
            for keyword in keywords:
                cursor.execute("SELECT Keyword_ID FROM Keyword WHERE Keyword = %s", (keyword,))
                keyword_data = cursor.fetchone()
                if keyword_data:
                    keyword_id = keyword_data[0]
                else:
                    cursor.execute("INSERT INTO Keyword (Keyword) VALUES (%s)", (keyword,))
                    keyword_id = cursor.lastrowid
            
                cursor.execute("INSERT INTO Book_Keyword (Keyword_ID, ISBN) VALUES (%s, %s)", (keyword_id, isbn))
                # Insert the record into the school_books table
        try:
            school_books_query = "INSERT INTO School_Books (ISBN, School_Name, Available_Copies) VALUES (%s, %s, %s)"
            school_books_values = (isbn, school_name[0],available_copies)
            cursor.execute(school_books_query, school_books_values)
        except mysql.connector.Error as error:
            if error.errno == 1062:
                error_message = 'Book already exists.'
            else:
                error_message = 'An error occurred. Check if all fields are correct or if the author needs to be distinguished using the ID.'
            return render_template('add_book.html', form=form, error_message= error_message)   
        # Commit the changes to the database
        connection.commit()
        success_message = "Book added successfully!"
        query_params = urlencode({"message": success_message})
        redirect_url = f"/operator/books?{query_params}"
        return redirect(redirect_url)
    
    return render_template('add_book.html', form=form)

@app.route('/operator/books/update_book/<isbn>', methods=['GET', 'POST'])
def update_book(isbn):
    form = BookForm()
    book = None
    username = session.get('username')
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query,(username,))
    school_name = cursor.fetchone()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            image_url = None  # default to None if no file is uploaded
            if form.image.data:
                image_file = form.image.data
                filename = secure_filename(image_file.filename)  # get the secure filename
                image_file.save(os.path.join('school_lib/static/images', filename))  # save the file
                image_url = 'images/' + filename  # update only if file is uploaded

            title = form.title.data
            num_pages = form.pages.data
            publisher = form.publisher.data
            language = form.language.data
            summary = form.summary.data
            authors = request.form.getlist('authors')
            categories = request.form.getlist('categories')
            keywords = request.form.getlist('keywords')
            available_copies = form.available_copies.data
        except AttributeError as error:
            error_message = 'An error occurred. Check if all fields are correct.'
            return render_template('books.html', error_message = error_message)
 
        # Update the book details

        cursor.execute("UPDATE School_Books SET Available_Copies = %s WHERE ISBN = %s AND School_Name = %s",
                       (available_copies,isbn,school_name[0]))
        
        # If no new image is uploaded, do not update Image_URL field
        if image_url:
            cursor.execute("UPDATE Book SET Title = %s, Number_Of_Pages = %s, Publisher = %s, Language = %s, "
                        "Summary = %s, Image_URL = %s WHERE ISBN = %s",
                        (title, num_pages, publisher, language, summary, image_url, isbn))
        else:
            cursor.execute("UPDATE Book SET Title = %s, Number_Of_Pages = %s, Publisher = %s, Language = %s, "
                        "Summary = %s WHERE ISBN = %s",
                        (title, num_pages, publisher, language, summary, isbn))
        
    
        # Remove existing book authors
        cursor.execute("DELETE FROM Book_Author WHERE ISBN = %s", (isbn,))

        # Insert/update the book authors into the Book_Author table
        authors = [author.strip() for author in ','.join(authors).split(',')]
        for author in authors:
            if ':' in author:
                author_info = author.split(':')
                if len(author_info) == 2:
                    author_id = author_info[0].strip()
                    first_name, last_name = [name.strip() for name in author_info[1].split()]
                else:
                    # Invalid author format, skip
                    continue
            else:
                first_name, last_name = [name.strip() for name in author.split()]
                author_id = None
            if author_id:
                cursor.execute("SELECT Author_ID FROM Author WHERE Author_ID = %s", (author_id,))
            else:
                cursor.execute("SELECT Author_ID FROM Author WHERE First_Name = %s AND Last_Name = %s",
                               (first_name, last_name))
            try:
                author_data = cursor.fetchone()
                if cursor.fetchone() is not None:
                    error_message = 'There are multiple authors with the same full name. Please provide the author ID.'
                    return render_template('update_book.html', form=form, book=book, authors=authors,
                        categories=categories, keywords=keywords, error_message = error_message)
            except mysql.connector.errors.InternalError as error:
                        error_message = 'An error occurred while fetching author data.'
                        return render_template('update_book.html', form=form, book=book, authors=authors,
                           categories=categories, keywords=keywords, error_message = error_message)
                      
    
            if author_data:
                author_id = author_data[0]
            else:
                cursor.execute("INSERT INTO Author (First_Name, Last_Name) VALUES (%s, %s)", (first_name, last_name))
                author_id = cursor.lastrowid

            cursor.execute("INSERT INTO Book_Author (Author_ID, ISBN) VALUES (%s, %s)", (author_id, isbn))

        # Remove existing book categories
        cursor.execute("DELETE FROM Book_Category WHERE ISBN = %s", (isbn,))

        # Insert/update the book categories into the Book_Category table
        categories = [category.strip() for category in ','.join(categories).split(',')]
        for category in categories:
            cursor.execute("SELECT Category_Id FROM Category WHERE Genre = %s", (category,))
            category_data = cursor.fetchone()
            if category_data:
                category_id = category_data[0]
            else:
                cursor.execute("INSERT INTO Category (Genre) VALUES (%s)", (category,))
                category_id = cursor.lastrowid

            cursor.execute("INSERT INTO Book_Category (Category_Id, ISBN) VALUES (%s, %s)", (category_id, isbn))

        # Remove existing book keywords
        cursor.execute("DELETE FROM Book_Keyword WHERE ISBN = %s", (isbn,))

        # Insert/update the book keywords into the Book_Keyword table
        keywords = [keyword.strip() for keyword in ','.join(keywords).split(',')]
        for keyword in keywords:
            cursor.execute("SELECT Keyword_ID FROM Keyword WHERE Keyword = %s", (keyword,))
            keyword_data = cursor.fetchone()
            if keyword_data:
                keyword_id = keyword_data[0]
            else:
                cursor.execute("INSERT INTO Keyword (Keyword) VALUES (%s)", (keyword,))
                keyword_id = cursor.lastrowid

            cursor.execute("INSERT INTO Book_Keyword (Keyword_ID, ISBN) VALUES (%s, %s)", (keyword_id, isbn))

        # Commit the changes to the database
        connection.commit()
        success_message = "Book updated successfully!"
        query_params = urlencode({"message": success_message})
        redirect_url = f"/operator/books?{query_params}"
        return redirect(redirect_url)
    
    # Retrieve the book details from the database
    cursor.execute("SELECT * FROM Book WHERE ISBN = %s", (isbn,))
    book = cursor.fetchone()

    cursor.execute("SELECT Available_Copies from School_Books WHERE ISBN = %s AND School_Name = %s", (isbn,school_name[0]))
    copies = cursor.fetchone()

    if book:
        # Populate the form with the existing book details
        form.title.data = book[1]
        form.pages.data = book[2]
        form.publisher.data = book[3]
        form.language.data = book[4]
        form.summary.data = book[5]
        form.image.data = url_for('static', filename=book[6])  # make sure the URL is correct
        form.available_copies.data = copies[0]


    # Retrieve the authors of the book
    cursor.execute("SELECT Author.First_Name, Author.Last_Name "
                   "FROM Book_Author JOIN Author ON Book_Author.Author_ID = Author.Author_ID "
                   "WHERE ISBN = %s", (isbn,))
    authors = cursor.fetchall()

    # Retrieve the categories of the book
    cursor.execute("SELECT Category.Genre FROM Book_Category JOIN Category ON "
                   "Book_Category.Category_Id = Category.Category_Id WHERE ISBN = %s", (isbn,))
    categories = cursor.fetchall()

    # Retrieve the keywords of the book
    cursor.execute("SELECT Keyword.Keyword FROM Book_Keyword JOIN Keyword ON "
                   "Book_Keyword.Keyword_ID = Keyword.Keyword_ID WHERE ISBN = %s", (isbn,))
    keywords = cursor.fetchall()

    return render_template('update_book.html', form=form, book=book, authors=authors,
                           categories=categories, keywords=keywords)



@app.route('/operator/reservations', methods=['GET','POST'])
def reservations_by_operator():
    operator_username = session.get("username")

    # Fetch the users connected to the operator's school
    users_query = "SELECT u.Username FROM User u INNER JOIN School s ON u.School_Name = s.Name INNER JOIN operator o ON s.Operator_id = o.Operator_ID WHERE o.Username = %s ORDER BY u.Username"
    cursor.execute(users_query, (operator_username,))
    users_result = cursor.fetchall()
    users = [row[0] for row in users_result]

    # Fetch the selected username from the request
    username = request.args.get("username")
    if username == "All Users":
        username = "_"

    # Construct the query to fetch reservations
    reservations_query = """
        SELECT u.user_id, u.Username, u.First_Name, u.Last_Name, r.Reservation_ID, r.Reservation_Date, r.ISBN, r.Is_Rented
        FROM User u
        INNER JOIN Book_Reservation r ON u.user_id = r.user_id
        INNER JOIN School s ON s.Name = u.School_Name
        INNER JOIN operator o ON o.Operator_ID = s.Operator_id
        WHERE o.Username = %s AND u.username LIKE CONCAT('%%', %s, '%%')
        ORDER BY r.Reservation_ID ASC
    """

    # Execute the query to fetch reservations
    cursor.execute(reservations_query, (operator_username, username))
    reservations_result = cursor.fetchall()
    reservations = [row for row in reservations_result]

    if request.method == 'POST':
        reservation_id = request.form.get("reservation_id")
        isbn = request.form.get("isbn")
        user_id = request.form.get("user_id")
        
        if reservation_id and isbn and user_id:
            try:
                # Insert into Rental table
                rental_insert_query = "INSERT INTO Rental (ISBN, User_ID, Rental_Date, Return_Date) VALUES (%s, %s, CURDATE(), NULL)"
                cursor.execute(rental_insert_query, (isbn, user_id))
                connection.commit()
            except mysql.connector.Error as err:
                if err.errno == 1644:  # MySQL error code for SIGNAL SQLSTATE '45000'
                    error_message = err.msg  # Retrieve the message_text sent by the trigger
                    return render_template('reservations_by_operator.html', username=operator_username, users=users, reservations=reservations, error_message=error_message)
                elif err.errno == 1690:
                    error_message = 'No available copies.'
                    return render_template('reservations_by_operator.html', username=operator_username, users=users, reservations=reservations, error_message=error_message)
                else:
                    error_message = 'Something went wrong.'
                    return render_template('reservations_by_operator.html', username=operator_username, users=users, reservations=reservations, error_message=error_message)


            
            # Update Book_Reservation table
            reservation_update_query = "UPDATE Book_Reservation SET Is_Rented = True WHERE Reservation_ID = %s"
            cursor.execute(reservation_update_query, (reservation_id,))
            connection.commit()

            success_message = "Reservation processed successfully!"
            return render_template('reservations_by_operator.html', username=operator_username,
                           users=users, reservations=reservations, success_message=success_message)

    return render_template('reservations_by_operator.html', username=operator_username,
                           users=users, reservations=reservations)

@app.route('/operator/not_overdue_rentals', methods=['GET'])
def not_overdue_rentals_by_operator():
    operator_username = session.get("username")

    # Fetch the users connected to the operator's school
    users_query = "SELECT u.Username FROM User u INNER JOIN School s ON u.School_Name = s.Name INNER JOIN operator o ON s.Operator_id = o.Operator_ID WHERE o.Username = %s ORDER BY u.Username"
    cursor.execute(users_query, (operator_username,))
    users_result = cursor.fetchall()
    users = [row[0] for row in users_result]

    # Fetch the selected username from the request
    username = request.args.get("username")
    if username == "All Users":
        username = "_"

    # Construct the query to fetch not overdue rentals
    rentals_query = """
        SELECT u.user_id, u.Username, u.First_Name, u.Last_Name, r.ISBN, r.Rental_ID, r.Rental_Date, r.Return_Date
        FROM User u
        INNER JOIN Rental r ON u.user_id = r.user_id
        INNER JOIN School s ON s.Name = u.School_Name
        INNER JOIN operator o ON o.Operator_ID = s.Operator_id
        WHERE o.Username = %s AND u.username LIKE CONCAT('%%', %s, '%%')
        AND (DATEDIFF(CURDATE(), r.Rental_Date) <= 7 OR r.Return_Date IS NOT NULL)
    """

    # Execute the query to fetch not overdue rentals
    cursor.execute(rentals_query, (operator_username, username))
    rentals_result = cursor.fetchall()
    rentals = [row for row in rentals_result]

    return render_template('not_overdue_rentals_by_operator.html', username=operator_username,
                           users=users, rentals=rentals)

@app.route('/operator/rentals', methods=['GET','POST'])
def rentals_by_operator():
    operator_username = session.get("username")

    # Fetch the users connected to the operator's school
    users_query = "SELECT u.Username FROM User u INNER JOIN School s ON u.School_Name = s.Name INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s ORDER BY u.Username"
    cursor.execute(users_query, (operator_username,))
    users_result = cursor.fetchall()
    users = [row[0] for row in users_result]

    # Fetch the selected username from the request
    username = request.args.get("username")
    if username == "All Users":
        username = "_"

    overdue_query = """
        SELECT DISTINCT u.User_ID, u.Username, u.First_Name, u.Last_Name, r.ISBN, r.Rental_ID, r.Rental_Date
        FROM User u
        INNER JOIN Rental r ON u.user_id = r.user_id
        INNER JOIN School s ON s.Name = u.School_Name
        INNER JOIN Operator o ON o.Operator_ID = s.Operator_ID
        WHERE r.Return_Date IS NULL AND DATEDIFF(CURDATE(), r.Rental_Date) > 7
        AND o.Username = %s AND u.username LIKE CONCAT('%%', %s, '%%')
        ORDER BY r.Rental_Date DESC
    """
    

    # Execute the query to fetch overdue rentals
    cursor.execute(overdue_query, (operator_username, username))
    overdue_result = cursor.fetchall()
    overdue_rentals = [row for row in overdue_result]

    # Construct the query to fetch not overdue rentals
    not_overdue_query = """
        SELECT u.user_id, u.Username, u.First_Name, u.Last_Name, r.ISBN, r.Rental_ID, r.Rental_Date, r.Return_Date
        FROM User u
        INNER JOIN Rental r ON u.user_id = r.user_id
        INNER JOIN School s ON s.Name = u.School_Name
        INNER JOIN Operator o ON o.Operator_ID = s.Operator_id
        WHERE o.Username = %s AND u.username LIKE CONCAT('%%', %s, '%%')
        AND (DATEDIFF(CURDATE(), r.Rental_Date) <= 7 OR r.Return_Date IS NOT NULL)
        ORDER BY r.Rental_Date DESC
    """

    # Execute the query to fetch not overdue rentals
    cursor.execute(not_overdue_query, (operator_username, username))
    not_overdue_result = cursor.fetchall()
    not_overdue_rentals = [row for row in not_overdue_result]

    if request.method == 'POST':
        action = request.form.get("action")
        
        if action == 'return':
            # handle rental returns
            isbn_param = request.form.get("isbn")
            user_id_param = request.form.get("user_id")
            if isbn_param and user_id_param:
                cursor.callproc('rental_return', [isbn_param, user_id_param])
                connection.commit()
                success_message = "Book returned successfully!"
        
        elif action == 'update':
            success_message = ''
            # handle rental record updates
            rental_id = request.form.get("rental_id")
            new_rental_date = request.form.get("new_rental_date")
            new_return_date = request.form.get("new_return_date")
            if rental_id and (new_rental_date or new_return_date):
                try:
                    if new_rental_date:
                        update_query = """
                            UPDATE Rental SET Rental_Date = %s WHERE Rental_ID = %s
                        """
                        cursor.execute(update_query, (new_rental_date, rental_id))
                        connection.commit()
                        success_message = "Rental Date updated successfully!"
                    if new_return_date:
                        update_query = """
                            UPDATE Rental SET Return_Date = %s WHERE Rental_ID = %s
                        """
                        cursor.execute(update_query, (new_return_date, rental_id))
                        connection.commit()
                        success_message += " Return Date updated successfully!"
                except mysql.connector.Error as err:
                    if err.errno == 3819: 
                        error_message = "Failed to update rental record: Return date must be later or equal to the rental date."
                        return render_template('rentals_by_operator.html', username=operator_username, users=users, not_overdue_rentals=not_overdue_rentals, overdue_rentals=overdue_rentals, error_message=error_message)
                    else:
                        error_message = "An error occurred while updating the rental record."
                        return render_template('rentals_by_operator.html', username=operator_username, users=users, not_overdue_rentals=not_overdue_rentals, overdue_rentals=overdue_rentals, error_message=error_message)


        elif action == 'delete':
            # handle rental record deletions
            rental_id = request.form.get("rental_id")
            if rental_id:
                delete_query = """
                    DELETE FROM Rental WHERE Rental_ID = %s
                """
                cursor.execute(delete_query, (rental_id,))
                connection.commit()
                success_message = "Rental record deleted successfully!"
                
        return render_template('rentals_by_operator.html', username=operator_username, users=users, not_overdue_rentals=not_overdue_rentals, overdue_rentals=overdue_rentals, success_message=success_message)

    return render_template('rentals_by_operator.html', username=operator_username, users=users, not_overdue_rentals=not_overdue_rentals, overdue_rentals=overdue_rentals)


@app.route('/operator/new_rentals', methods=['GET', 'POST'])
def operator_books():
    search_query = request.args.get('search')
    operator_username = session.get("username")
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query,(operator_username,))
    school_name = cursor.fetchone()

    if search_query:
        # Handle the search query
        cursor.execute("SELECT b.ISBN, b.Title, b.Publisher, "
                       "GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name, ' (ID: ', a.Author_ID, ')')) AS Authors, "
                       "(SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = %s) as Available_Copies "
                       "FROM Book b "
                       "JOIN School_Books sb ON b.ISBN = sb.ISBN "
                       "JOIN School s ON sb.School_Name = s.Name "
                       "JOIN Operator o ON s.Operator_ID = o.Operator_ID "
                       "LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN "
                       "LEFT JOIN Author a ON ba.Author_ID = a.Author_ID "
                       "LEFT JOIN Book_Keyword bk ON b.ISBN = bk.ISBN "
                       "LEFT JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID "
                       "LEFT JOIN Book_Category bc ON b.ISBN = bc.ISBN "
                       "LEFT JOIN Category c ON bc.Category_Id = c.Category_Id "
                       "WHERE b.Title LIKE CONCAT('%', %s, '%') "
                       "AND o.username = %s "
                       "GROUP BY b.ISBN", (school_name[0],search_query, operator_username))
        books_data = cursor.fetchall()
    else:
        # Fetch books from the operator's school
        cursor.execute("SELECT b.ISBN, b.Title, b.Publisher, "
                       "GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name, ' (ID: ', a.Author_ID, ')')) AS Authors, "
                       "(SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = %s) as Available_Copies "
                       "FROM Book b "
                       "JOIN School_Books sb ON b.ISBN = sb.ISBN "
                       "JOIN School s ON sb.School_Name = s.Name "
                       "JOIN Operator o ON s.Operator_ID = o.Operator_ID "
                       "LEFT JOIN Book_Author ba ON b.ISBN = ba.ISBN "
                       "LEFT JOIN Author a ON ba.Author_ID = a.Author_ID "
                       "LEFT JOIN Book_Keyword bk ON b.ISBN = bk.ISBN "
                       "LEFT JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID "
                       "LEFT JOIN Book_Category bc ON b.ISBN = bc.ISBN "
                       "LEFT JOIN Category c ON bc.Category_Id = c.Category_Id "
                       "WHERE o.username = %s "
                       "GROUP BY b.ISBN", (school_name[0],operator_username))
        books_data = cursor.fetchall()

    # Fetch the users connected to the operator's school
    users_query = "SELECT u.Username FROM User u INNER JOIN School s ON u.School_Name = s.Name INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s ORDER BY USERNAME"
    cursor.execute(users_query, (operator_username,))
    users_result = cursor.fetchall()
    users = [row[0] for row in users_result]

    if request.method == 'POST':
        isbn = request.form['isbn']
        username = request.form['username']
        try:
            cursor.execute("CALL create_rental(%s, %s)", (isbn, username))
            connection.commit()
        except mysql.connector.Error as err:
                if err.errno == 1644:  
                    error_message = err.msg  
                    return render_template('operator_books.html', books=books_data, users=users, error_message=error_message)
                elif err.errno == 1690:
                    error_message = 'No available copies.'
                    return render_template('operator_books.html', books=books_data, users=users, error_message=error_message)
                else:
                    error_message = 'Something went wrong. Ensure that you select a user.' 
                    return render_template('operator_books.html', books=books_data, users=users, error_message=error_message)

        return redirect(url_for('operator_books', message='Rental added successfully'))

    message = request.args.get("message")
    return render_template('operator_books.html', books=books_data, users=users, message=message)

@app.route('/operator/users', methods=['GET', 'POST'])
def operator_users():
    operator_username = session.get("username")

    # Fetch all users of the operator's school with additional details
    users_query = "SELECT u.User_ID, u.Username, u.First_Name, u.Last_Name, u.Email, u.School_Name, " \
                  "u.Date_of_Birth, u.Is_Teacher " \
                  "FROM User u " \
                  "INNER JOIN School s ON u.School_Name = s.Name " \
                  "INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID " \
                  "WHERE o.Username = %s " \
                  "GROUP BY u.User_ID"
    cursor.execute(users_query, (operator_username,))
    users_result = cursor.fetchall()
    users = []
    for row in users_result:
        user = {
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'email': row[4],
            'school_name': row[5],
            'date_of_birth': row[6].strftime('%Y-%m-%d'),
            'is_teacher': bool(row[7])
        }
        users.append(user)

    pending_query = "SELECT pr.Registration_ID, pr.Username, pr.First_Name, pr.Last_Name, pr.Email, pr.School_Name, " \
                    "pr.Date_of_Birth, pr.Is_Teacher, pr.Password " \
                    "FROM Pending_Registrations pr " \
                    "INNER JOIN School s ON pr.School_Name = s.Name " \
                    "INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID " \
                    "WHERE o.Username = %s "
    cursor.execute(pending_query, (operator_username,))
    pending_result = cursor.fetchall()
    pending_users = []
    for row in pending_result:
        pending_user = {
            'registration_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'email': row[4],
            'school_name': row[5],
            'date_of_birth': row[6].strftime('%Y-%m-%d'),
            'is_teacher': bool(row[7]),
            'password': row[8]
        }
        pending_users.append(pending_user)

    if request.method == 'POST':
        action_type = request.form['action_type'] 
        if action_type == "delete":
            user_id = request.form['user_id']
            # Delete the selected user from the database
            delete_query = "DELETE FROM User WHERE User_ID = %s"
            cursor.execute(delete_query, (user_id,))
            message='User deleted successfully'
        elif action_type == "accept":
            registration_id = request.form['registration_id']
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            school_name = request.form['school_name']
            date_of_birth = request.form['date_of_birth']
            is_teacher = request.form['is_teacher']
            insert_query = "INSERT INTO User (Username, Password, First_Name, Last_Name, Email, School_Name, Date_Of_Birth, Is_Teacher) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (username, password, first_name, last_name, email, school_name, date_of_birth, is_teacher))
           
            connection.commit()
            delete_query = "DELETE FROM Pending_Registrations WHERE Registration_ID = %s"
            cursor.execute(delete_query, (registration_id,))
            message='User accepted successfully'
        elif action_type == "decline":
            registration_id = request.form['registration_id']
            delete_query = "DELETE FROM Pending_Registrations WHERE Registration_ID = %s"
            cursor.execute(delete_query, (registration_id,))
            message='User declined successfully'
        else:
            message='Unknown action type'
        connection.commit()
        return render_template('operator.html', username = operator_username, message=message)

    message = request.args.get("message")
    return render_template('operator_users.html', users=users, pending_users=pending_users, message=message)

@app.route('/user/books', methods=['GET', 'POST'])
def user_books():
    user_username = session.get("username")
    search_title = request.args.get('search_title')
    search_category = request.args.get('search_category')
    search_author_first_name = request.args.get('search_author_first_name')
    search_author_last_name = request.args.get('search_author_last_name')
    query = "SELECT School_Name FROM User WHERE Username = %s"
    cursor.execute(query,(user_username,))
    school_name = cursor.fetchone()

    query = """
        SELECT DISTINCT b.ISBN
        FROM User u
        INNER JOIN School_Books sb ON sb.School_Name = u.School_Name
        INNER JOIN Book b ON sb.ISBN = b.ISBN
        INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
        INNER JOIN Author a ON a.Author_ID = ba.Author_ID
        INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
        INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
        INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
        INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
        WHERE u.username = %s
        AND b.Title LIKE CONCAT('%%', %s, '%%')
        AND c.Genre LIKE CONCAT('%%', %s, '%%')
        AND a.First_Name LIKE CONCAT('%%', %s, '%%')
        AND a.Last_Name LIKE CONCAT('%%', %s, '%%')
    """

    params = [user_username, search_title, search_category, search_author_first_name, search_author_last_name]

    cursor.execute(query, params)
    isbn_list = [item[0] for item in cursor.fetchall()]
    books = []

    if isbn_list:
        query = """
            SELECT b.ISBN, b.Title, b.Image_URL, 
            GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name) SEPARATOR ', ') AS Authors,
            GROUP_CONCAT(DISTINCT c.Genre SEPARATOR ', ') AS Genres,
            GROUP_CONCAT(DISTINCT k.Keyword SEPARATOR ', ') AS Keywords,
            (SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = '%s') as Available_Copies,
            b.Summary
            FROM User u
            INNER JOIN School_Books sb ON sb.School_Name = u.School_Name
            INNER JOIN Book b ON sb.ISBN = b.ISBN
            INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
            INNER JOIN Author a ON a.Author_ID = ba.Author_ID
            INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
            INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
            INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
            INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
            WHERE b.ISBN IN (%s)
            GROUP BY b.ISBN
        """

        formatted_isbn_list = ', '.join(['%s'] * len(isbn_list)) # Creates a string of '%s' separated by commas to use as placeholders in the IN clause.
        query = query % (school_name[0], formatted_isbn_list) # Replaces the '%s' in the IN clause with the correct number of placeholders.
        params = isbn_list # Uses the list of ISBNs as parameters for the second query.

        cursor.execute(query, params)
        books_data = cursor.fetchall()

    
        for book in books_data:
            book_item = {
                'isbn': book[0],
                'title': book[1],
                'image_url': book[2],
                'authors': book[3],
                'genres': book[4],
                'keywords': book[5],
                'available_copies': book[6],
                'summary' : book[7]
            }
            books.append(book_item)

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        username = session.get("username")

        # Retrieve the user_id from the User table based on the username
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s", (username,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            try:
                query = "INSERT INTO book_reservation (ISBN, User_ID, Reservation_Date) VALUES (%s, %s, CURDATE())"
                values = (isbn, user_id)
                cursor.execute(query, values)
                connection.commit()
            except mysql.connector.Error as err:
                if err.errno == 1644:  
                    error_message = err.msg  
                    return render_template('user_books.html', error_message=error_message)

            return render_template('user_books.html', message='Reservation added successfully')
    search_performed = any([search_title, search_category, search_author_first_name, search_author_last_name])
    message = request.args.get("message")
    return render_template('user_books.html', books=books, message=message, search_performed=search_performed)


@app.route('/user/create_review', methods=['POST'])
def create_review():
    user_username = session.get("username")
    isbn = request.form.get('isbn')
    review_text = request.form.get('review_text')
    likert_review = request.form.get('likert_review')

    # Retrieve the user_id from the User table based on the username
    cursor.execute("SELECT User_ID FROM User WHERE Username = %s", (user_username,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        query = "INSERT INTO Book_Review (ISBN, User_ID, Review_Text, Review_Date, Likert_Review) " \
                "VALUES (%s, %s, %s, CURDATE(), %s)"
        values = (isbn, user_id, review_text, likert_review)
        cursor.execute(query, values)
        connection.commit()
        return redirect(url_for('user_books', message='Review added successfully'))
    else:
        return redirect(url_for('user_books', message='Failed to add review'))


@app.route('/teacher/profile', methods=['GET', 'POST'])
def teacher_profile():

    username = session.get('username')
    cursor.execute("SELECT User_ID FROM User WHERE Username = %s", (username,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]

    if request.method == 'POST':
        # Update the user's data based on the form submission
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        date_of_birth = request.form['date_of_birth']
        
        # Perform the necessary database update query to update the user's data
        try:
            update_query = "UPDATE User SET First_Name = %s, Last_Name = %s, Email = %s, Date_of_Birth = %s WHERE User_ID = %s"
            cursor.execute(update_query, (first_name, last_name, email, date_of_birth, user_id))
            connection.commit()
        except mysql.connector.Error as err:
            if err.errno == 1644:  
                error_message = err.msg  
                return render_template('teacher.html',username = username, error_message=error_message)
            else:
                error_message = 'Something went wrong'
                return render_template('teacher.html',username = username, error_message=error_message)
       
        # Redirect to the updated teacher profile page or show a success message
        return render_template('teacher.html',username = username, message='Profile updated successfully')

    # Fetch the user's current data from the database
    cursor.execute("SELECT * FROM User WHERE User_ID = %s", (user_id,))
    user_data = cursor.fetchone()


    # Prepare the user's current data for rendering in the template
    user = {
        'user_id': user_data[0],
        'first_name': user_data[3],
        'last_name': user_data[4],
        'email': user_data[5],
        'date_of_birth': user_data[7].strftime('%Y-%m-%d') 
    
    }

    message = request.args.get('message')
    return render_template('teacher_profile.html', user=user, message=message)

@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    user_username = session.get("username")

    # Retrieve user's reservations
    query = "SELECT b.ISBN, b.Title, r.Reservation_Date " \
            "FROM Book_Reservation r " \
            "INNER JOIN Book b ON r.ISBN = b.ISBN " \
            "INNER JOIN User u ON r.User_ID = u.User_ID " \
            "WHERE u.Username = %s"
    cursor.execute(query, (user_username,))
    reservations_data = cursor.fetchall()

    reservations = []
    for reservation in reservations_data:
        reservation_item = {
            'isbn': reservation[0],
            'title': reservation[1],
            'reservation_date': reservation[2].strftime('%Y-%m-%d')
        }
        reservations.append(reservation_item)

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        username = session.get("username")
        cursor.execute("SELECT User_ID FROM User WHERE Username = %s", (username,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]

        # Delete the reservation
        query = "DELETE FROM Book_Reservation WHERE ISBN = %s AND User_ID = %s"
        cursor.execute(query, (isbn, user_id))
        connection.commit()
        return redirect(url_for('user_reservations', message='Reservation canceled successfully'))

    message = request.args.get("message")
    return render_template('user_reservations.html', reservations=reservations, message=message)

@app.route('/operator/reviews', methods=['GET', 'POST'])
def operator_reviews():
    operator_username = session.get("username")

    # Retrieve operator's school name
    cursor.execute("SELECT Name FROM School s "
            "INNER JOIN Operator o ON o.Operator_ID = s.Operator_ID "
            "WHERE o.Username = %s", (operator_username,))
    result = cursor.fetchone()

    if not result:
        return "Operator not found"

    # Retrieve book reviews from students in the operator's school
    query = "SELECT r.Review_ID, b.Title, u.Username, r.Review_Text, r.Review_Date, r.Likert_Review " \
            "FROM Book_Review r " \
            "INNER JOIN Book b ON r.ISBN = b.ISBN " \
            "INNER JOIN User u ON r.User_ID = u.User_ID " \
            "WHERE u.School_Name = %s"
    cursor.execute(query, (result[0],))
    reviews_data = cursor.fetchall()

    reviews = []
    for review in reviews_data:
        review_item = {
            'review_id': review[0],
            'title': review[1],
            'username': review[2],
            'review_text': review[3],
            'review_date': review[4].strftime('%Y-%m-%d'),
            'likert_review': review[5]
        }
        reviews.append(review_item)

    if request.method == 'POST':
        review_id = request.form.get('review_id')
        action = request.form.get('action')

        if action == 'publish':
            # Retrieve the review data
            cursor.execute("SELECT ISBN, User_ID, Review_Text, Review_Date, Likert_Review FROM Book_Review WHERE Review_ID = %s", (review_id,))
            review_data = cursor.fetchone()
            if review_data:
                # Insert the review into the Published_Book_Review table
                insert_query = "INSERT INTO Published_Book_Review (ISBN, User_ID, Review_Text, Review_Date, Likert_Review) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query, review_data)
                connection.commit()
                # Delete the review from the Book_Review table
                delete_query = "DELETE FROM Book_Review WHERE Review_ID = %s"
                cursor.execute(delete_query, (review_id,))
                connection.commit()
                return render_template('operator.html',username = operator_username, message='Review published successfully')

        elif action == 'delete':
            # Delete the review from the Book_Review table
            delete_query = "DELETE FROM Book_Review WHERE Review_ID = %s"
            cursor.execute(delete_query, (review_id,))
            connection.commit()
            return render_template('operator.html',username = operator_username, message='Review deleted successfully')

    message = request.args.get("message")
    return render_template('operator_reviews.html', reviews=reviews, message=message)

@app.route('/operator/published_book_reviews')
def published_book_reviews():
    operator_username = session.get('username')
    cursor.execute("SELECT Name FROM School s "
        "INNER JOIN Operator o ON o.Operator_ID = s.Operator_ID "
        "WHERE o.Username = %s", (operator_username,))
    result = cursor.fetchone()
    # Query to fetch all published book reviews
    reviews_query = """
        SELECT r.Published_Review_ID, r.ISBN, b.Title, u.User_ID, u.Username, r.Review_Text, r.Review_Date, r.Likert_Review
        FROM Published_Book_Review r
        INNER JOIN User u ON r.User_ID = u.User_ID
        INNER JOIN Book b ON r.ISBN = B.ISBN
        WHERE u.School_Name = %s
        ORDER BY r.Review_Date DESC
    """
    cursor.execute(reviews_query,(result[0],))
  
    reviews = cursor.fetchall()
    message = request.args.get("message")
    return render_template('published_book_reviews.html', reviews=reviews, message = message)

@app.route('/user/published_book_reviews',methods=['GET', 'POST'])
def user_published_book_reviews():
    username = session.get('username')
    title_search = request.args.get("title_search", "")

    query = 'SELECT School_Name FROM User WHERE Username = %s'
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    # Query to fetch all published book reviews
    reviews_query = """
        SELECT  b.Title, u.Username, r.Review_Text, r.Review_Date, r.Likert_Review
        FROM Published_Book_Review r
        INNER JOIN User u ON r.User_ID = u.User_ID
        INNER JOIN Book b ON b.ISBN = r.ISBN
        WHERE u.School_Name = %s AND b.Title LIKE %s
        ORDER BY r.Review_Date DESC
    """
    cursor.execute(reviews_query, (result[0], "%" + title_search + "%"))
    reviews = cursor.fetchall()

    message = request.args.get("message")

    return render_template('user_published_book_reviews.html', reviews=reviews, message=message, title_search=title_search)

@app.route('/operator/delete_published_review/<int:review_id>', methods=['POST'])
def delete_published_review(review_id):
    username = session.get('username')
    
    delete_query = """
        DELETE FROM Published_Book_Review WHERE Published_Review_ID = %s
    """
    cursor.execute(delete_query, (review_id,))
    connection.commit()
    message = 'Review Deleted Succesfully'
    return render_template('operator.html',username = username, message= message)


@app.route('/administrator/rentals_by_school', methods=['GET', 'POST'])
def get_rentals_by_school():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        query = "SELECT School.Name, COUNT(*) as Total_Rentals " \
                "FROM Rental " \
                "INNER JOIN User ON Rental.User_ID = User.User_ID " \
                "INNER JOIN School ON User.School_Name = School.Name " \
                "WHERE Rental.Rental_Date BETWEEN %s AND %s " \
                "GROUP BY School.Name " \
                "ORDER BY School.Name "

        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchall()

        rentals_by_school = []
        for row in result:
            school_name = row[0]
            total_rentals = row[1]
            rentals_by_school.append({'school_name': school_name, 'total_rentals': total_rentals})

        return render_template('rentals_by_school.html', rentals_by_school=rentals_by_school)

    return render_template('rentals_by_school_form.html')


@app.route('/administrator/query_authors_teachers_categories', methods=['GET', 'POST'])
def query_authors_teachers_categories():
    if request.method == 'POST':
        genre = request.form.get('genre')
        authors_query = "SELECT DISTINCT Author.Author_ID, Author.First_Name, Author.Last_Name " \
                        "FROM Author " \
                        "INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID " \
                        "INNER JOIN Book_Category ON Book_Author.ISBN = Book_Category.ISBN " \
                        "INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id " \
                        "WHERE Category.Genre = %s" \
                        "ORDER BY Author.First_Name, Author.Last_Name"
        cursor.execute(authors_query, (genre,))
        authors = cursor.fetchall()

        teachers_query = "SELECT DISTINCT User.User_ID, User.Username, User.First_Name, User.Last_Name, User.School_Name " \
                         "FROM User " \
                         "INNER JOIN Rental ON User.User_ID = Rental.User_ID " \
                         "INNER JOIN Book_Category ON Rental.ISBN = Book_Category.ISBN " \
                         "INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id " \
                         "WHERE Category.Genre = %s " \
                         "AND User.Is_Teacher = TRUE " \
                         "AND Rental.Rental_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)" \
                         "ORDER BY User.Username"
        cursor.execute(teachers_query, (genre,))
        teachers = cursor.fetchall()

        return render_template('authors_teachers_categories_results.html', authors=authors, teachers=teachers)

    # Fetch the categories from the database
    cursor.execute("SELECT Genre FROM Category")
    categories = cursor.fetchall()
    
    return render_template('authors_teachers_categories.html', categories=categories)

@app.route('/administrator/teachers_rentals', methods=['GET'])
def get_teachers_rentals():
    query = "SELECT User.User_ID, User.First_Name, User.Last_Name, User.School_Name, COUNT(*) AS Number_Of_Rentals " \
            "FROM User " \
            "INNER JOIN Rental ON User.User_ID = Rental.User_ID " \
            "WHERE User.Is_Teacher = TRUE " \
            "AND User.Date_Of_Birth > DATE_SUB(CURDATE(), INTERVAL 40 YEAR) " \
            "GROUP BY User_ID " \
            "ORDER BY Number_Of_Rentals DESC " \
            "LIMIT 20"

    cursor.execute(query)
    result = cursor.fetchall()

    teachers_rentals = []
    for row in result:
        user_id = row[0]
        first_name = row[1]
        last_name = row[2]
        school_name = row[3]
        number_of_rentals = row[4]
        teachers_rentals.append({'user_id': user_id, 'first_name': first_name, 'last_name': last_name,'school_name' :school_name, 'number_of_rentals': number_of_rentals})

    return render_template('teachers_rentals.html', teachers_rentals=teachers_rentals)


@app.route('/administrator/authors_with_no_rentals', methods=['GET'])
def get_authors_with_no_rentals():
    query = "SELECT Author.Author_ID, Author.First_Name, Author.Last_Name " \
            "FROM Author " \
            "INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID " \
            "LEFT JOIN Rental ON Book_Author.ISBN = Rental.ISBN " \
            "GROUP BY Author.Author_ID " \
            "HAVING COUNT(Rental.Rental_ID) = 0 " \
            "ORDER BY Author.First_Name, Author.Last_Name"
    
    cursor.execute(query)
    authors = cursor.fetchall()

    return render_template('authors_with_no_rentals.html', authors=authors)



@app.route('/administrator/high_activity_operators', methods=['GET', 'POST'])
def high_activity_operators():
    if request.method == 'POST':
        year = int(request.form.get('year'))
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        query = "SELECT o.Operator_ID,o.username, o.First_Name, o.Last_Name, COUNT(*) AS Num_Rentals " \
                "FROM Operator o " \
                "INNER JOIN School s ON o.Operator_ID = s.Operator_id " \
                "INNER JOIN User u ON s.Name = u.School_Name " \
                "INNER JOIN Rental r ON r.User_ID = u.User_ID " \
                "WHERE r.Rental_Date BETWEEN %s AND %s " \
                "GROUP BY o.Operator_ID " \
                "HAVING Num_Rentals > 20 " \
                "AND COUNT(*) = SOME( " \
                "SELECT COUNT(*) " \
                "FROM Operator o1 " \
                "INNER JOIN School s1 ON o1.Operator_ID = s1.Operator_id " \
                "INNER JOIN User u1 ON s1.Name = u1.School_Name " \
                "INNER JOIN Rental r1 ON r1.User_ID = u1.User_ID " \
                "WHERE r1.Rental_Date BETWEEN %s AND %s " \
                "AND o.Operator_ID <> o1.Operator_ID " \
                "GROUP BY o1.Operator_ID) " \
                "ORDER BY Num_Rentals DESC"

        cursor.execute(query, (start_date, end_date, start_date, end_date))
        result = cursor.fetchall()

        high_activity_operators = []
        for row in result:
            operator_id = row[0]
            username = row[1]
            first_name = row[2]
            last_name = row[3]
            num_rentals = row[4]
            high_activity_operators.append({'operator_id': operator_id, 'username' : username, 'first_name': first_name,
                                            'last_name': last_name, 'num_rentals': num_rentals})

        return render_template('high_activity_operators.html', operators=high_activity_operators)

    return render_template('high_activity_operators_form.html')

@app.route('/administrator/top_category_combinations', methods=['GET'])
def top_category_combinations():
    query = "SELECT c1.Genre AS Category1, c2.Genre AS Category2, COUNT(*) AS Num_Rentals " \
            "FROM Rental r " \
            "INNER JOIN Book b ON b.ISBN = r.ISBN " \
            "INNER JOIN Book_Category bc1 ON bc1.ISBN = b.ISBN " \
            "INNER JOIN Category c1 ON c1.Category_ID = bc1.Category_ID " \
            "INNER JOIN Book_Category bc2 ON bc2.ISBN = b.ISBN " \
            "INNER JOIN Category c2 ON c2.Category_ID = bc2.Category_ID " \
            "WHERE c1.Category_ID < c2.Category_ID " \
            "GROUP BY c1.Category_ID, c2.Category_ID " \
            "HAVING COUNT(*) > 0 " \
            "ORDER BY Num_Rentals DESC " \
            "LIMIT 3"

    cursor.execute(query)
    results = cursor.fetchall()

    categories = []
    for row in results:
        category1 = row[0]
        category2 = row[1]
        num_rentals = row[2]
        categories.append({'category1': category1, 'category2': category2, 'num_rentals': num_rentals})

    return render_template('top_category_combinations.html', categories=categories)

@app.route('/administrator/authors_fewer_books', methods=['GET'])
def authors_fewer_books():
    query = "SELECT a1.Author_ID, a1.First_Name, a1.Last_Name, COUNT(*) AS Books_Written " \
            "FROM Author a1 " \
            "INNER JOIN Book_Author ba1 ON a1.Author_ID = ba1.Author_ID " \
            "GROUP BY a1.Author_ID " \
            "HAVING COUNT(*) <= (SELECT COUNT(*) " \
            "                   FROM Author a2 " \
            "                   INNER JOIN Book_Author ba2 ON a2.Author_ID = ba2.Author_ID " \
            "                   GROUP BY a2.Author_ID " \
            "                   ORDER BY COUNT(*) DESC " \
            "                   LIMIT 1) - 5 " \
            "ORDER BY Books_Written DESC"
    
    cursor.execute(query)
    result = cursor.fetchall()

    authors = []
    for row in result:
        author = {
            'id' : row[0],
            'first_name': row[1],
            'last_name': row[2],
            'books_written': row[3]
        }
        authors.append(author)

    return render_template('authors_fewer_books.html', authors=authors)


@app.route('/operator/search_books', methods=['GET', 'POST'])
def search_operator_books():
    operator_username = session.get("username")
    search_title = request.args.get('search_title')
    search_category = request.args.get('search_category')
    search_author_first_name = request.args.get('search_author_first_name')
    search_author_last_name = request.args.get('search_author_last_name')
    search_available_copies = request.args.get('search_available_copies')
    try:
        search_available_copies = int(search_available_copies) if search_available_copies else None
    except ValueError:
        search_available_copies = 0
    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query,(operator_username,))
    school_name = cursor.fetchone()

    query = """
        SELECT DISTINCT b.ISBN
        FROM Operator o
        INNER JOIN School s ON s.operator_id = o.operator_id
        INNER JOIN School_Books sb ON sb.School_Name = s.Name
        INNER JOIN Book b ON sb.ISBN = b.ISBN
        INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
        INNER JOIN Author a ON a.Author_ID = ba.Author_ID
        INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
        INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
        INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
        INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
        WHERE o.username = %s
        AND b.Title LIKE CONCAT('%%', %s, '%%')
        AND c.Genre LIKE CONCAT('%%', %s, '%%')
        AND a.First_Name LIKE CONCAT('%%', %s, '%%')
        AND a.Last_Name LIKE CONCAT('%%', %s, '%%')
        AND (sb.Available_Copies >= %s)
    """

    params = [operator_username, search_title, search_category, search_author_first_name, search_author_last_name,search_available_copies]

    cursor.execute(query, params)
    isbn_list = [item[0] for item in cursor.fetchall()]

    books = []
    if isbn_list:
        query = """
            SELECT b.ISBN, b.Title, b.Image_URL, 
            GROUP_CONCAT(DISTINCT CONCAT(a.First_Name, ' ', a.Last_Name) SEPARATOR ', ') AS Authors,
            GROUP_CONCAT(DISTINCT c.Genre SEPARATOR ', ') AS Genres,
            GROUP_CONCAT(DISTINCT k.Keyword SEPARATOR ', ') AS Keywords,
            (SELECT Available_Copies FROM School_Books WHERE ISBN = b.ISBN AND School_NAME = '%s') as Available_Copies,
            b.Summary
            FROM Operator o
            INNER JOIN School s ON s.operator_id = o.operator_id
            INNER JOIN School_Books sb ON sb.School_Name = s.Name
            INNER JOIN Book b ON sb.ISBN = b.ISBN
            INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
            INNER JOIN Author a ON a.Author_ID = ba.Author_ID
            INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
            INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
            INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
            INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
            WHERE b.ISBN IN (%s)
            GROUP BY b.ISBN
        """

        formatted_isbn_list = ', '.join(['%s'] * len(isbn_list)) # Creates a string of '%s' separated by commas to use as placeholders in the IN clause.
        query = query % (school_name[0], formatted_isbn_list) # Replaces the '%s' in the IN clause with the correct number of placeholders.
        params = isbn_list # Uses the list of ISBNs as parameters for the second query.

        cursor.execute(query, params)
        books_data = cursor.fetchall()
        

  
        for book in books_data:
            book_item = {
                'isbn': book[0],
                'title': book[1],
                'image_url' : book[2],
                'authors': book[3],
                'genres': book[4],
                'keywords': book[5],
                'available_copies': book[6],
                'summary' : book[7]
            }
         
            books.append(book_item)


    search_performed = any([search_title, search_category, search_author_first_name, search_author_last_name])
    message = request.args.get("message")
    return render_template('search_books.html', books=books, message=message, search_performed=search_performed)



@app.route('/operator/overdue_rentals', methods=['GET', 'POST'])
def get_overdue_rentals():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    delay_date = request.args.get('delay_date')
    operator = session.get('username')

    query = "SELECT s.Name FROM School s INNER JOIN Operator o ON s.Operator_ID = o.Operator_ID WHERE o.Username = %s"
    cursor.execute(query,(operator,))
    school_name = cursor.fetchone()


    query = """
        SELECT DISTINCT u.User_ID, u.Username, u.First_Name, u.Last_Name
        FROM User u
        INNER JOIN Rental r
        ON u.user_id = r.user_id
        WHERE r.Return_Date IS NULL AND DATEDIFF(CURDATE(), r.Rental_Date) > 7
        AND u.First_Name LIKE CONCAT('%%', %s, '%%')
        AND u.Last_Name LIKE CONCAT('%%', %s, '%%')
        AND DATEDIFF(CURDATE(), r.Rental_Date ) >=  7 + %s
        AND u.School_Name = %s
    """

    params = [first_name, last_name, delay_date, school_name[0]]

    cursor.execute(query, params)
    rentals = cursor.fetchall()

    return render_template('overdue_rentals.html', rentals=rentals)


@app.route('/operator/avg_reviews_per_category', methods=['GET', 'POST'])
def avg_reviews_per_category():
    genre = request.args.get('genre')
    user_username = request.args.get('user_username')
    operator_id = session.get('id')
    query = 'SELECT Name FROM School WHERE Operator_ID = %s'
    cursor.execute(query,(operator_id,))
    result = cursor.fetchone()

    query = """
        SELECT User.User_ID, User.Username, Category.Genre, AVG(Published_Book_Review.Likert_Review) AS avg_reviews_per_user_and_category
        FROM User 
        INNER JOIN Published_Book_Review ON User.User_ID = Published_Book_Review.User_ID 
        INNER JOIN Book_Category ON Published_Book_Review.ISBN = Book_Category.ISBN 
        INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id 
        WHERE Category.Genre LIKE CONCAT('%%', %s, '%%')
        AND User.Username LIKE CONCAT('%%', %s, '%%')
        AND User.School_Name = %s
        GROUP BY User.User_ID, Category.Category_ID
    """

    params = [genre, user_username, result[0]]

    cursor.execute(query, params)
    reviews = cursor.fetchall()

    user_query = """
        SELECT u.Username 
        FROM USER u
        WHERE u.School_Name = %s
        ORDER BY u.Username
    """
    cursor.execute(user_query, (result[0],))
    users = [user[0] for user in cursor.fetchall()]

    # Fetch categories
    category_query = "SELECT Genre FROM Category ORDER BY GENRE"
    cursor.execute(category_query)
    categories = [category[0] for category in cursor.fetchall()]

    return render_template('avg_reviews_per_category.html',genres = categories,users = users, reviews=reviews)

@app.route('/operator/avg_reviews', methods=['GET', 'POST'])
def avg_reviews():
    user_username = request.args.get('user_username')
    genre = request.args.get('genre')
    operator_id = session.get('id')
    query = 'SELECT Name FROM School WHERE Operator_ID = %s'
    cursor.execute(query,(operator_id,))
    result = cursor.fetchone()

    user_query = """
        SELECT User.User_ID, User.Username, User.First_Name, User.Last_Name, AVG(Published_Book_Review.Likert_Review) 
        FROM User
        INNER JOIN Published_Book_Review ON User.User_ID = Published_Book_Review.User_ID
        WHERE User.Username = %s
        GROUP BY User.User_ID
    """
    cursor.execute(user_query, (user_username,))
    user_reviews = cursor.fetchall()

    category_query = """
        SELECT Category.Genre, AVG(Published_Book_Review.Likert_Review)
        FROM Category 
        INNER JOIN Book_Category ON Category.Category_ID = Book_Category.Category_ID
        INNER JOIN Published_Book_Review ON Book_Category.ISBN = Published_Book_Review.ISBN
        INNER JOIN User ON Published_Book_Review.User_ID = User.User_ID
        WHERE Category.Genre = %s
        AND User.School_Name = %s
        GROUP BY Category.Category_ID
    """
    cursor.execute(category_query, (genre,result[0]))
    category_reviews = cursor.fetchall()

    cursor.execute("SELECT Username FROM USER WHERE School_Name = %s ORDER BY Username", (result[0],))
    users = [user[0] for user in cursor.fetchall()]

    cursor.execute("SELECT Genre FROM Category ORDER BY Genre")
    genres = [genre[0] for genre in cursor.fetchall()]


    return render_template('avg_reviews.html',users=users, user_reviews=user_reviews, genres=genres, category_reviews=category_reviews)


@app.route('/user/books_by_user', methods=['GET', 'POST'])
def books_by_user():
    username = session.get('username')

    query = """
        SELECT DISTINCT  Book.ISBN, Book.Title, Rental.Rental_Date, Rental.Return_Date
        FROM Rental
        INNER JOIN Book ON Rental.ISBN = Book.ISBN
        INNER JOIN User ON Rental.User_ID = User.User_ID
        WHERE User.Username = %s
        ORDER BY Rental.Rental_Date DESC
    """

    cursor.execute(query, (username,))
    books = cursor.fetchall()

    return render_template('books_by_user.html', books=books)


    
