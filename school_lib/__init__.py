## This file is ran automatically the first time a Python program  imports the package school_lib
from flask import Flask
import mysql.connector


## __name__ is the name of the module. When running directly from python, it will be 'school_lib'
## Outside of this module, as in run.py, it is '__main__' by default
## Create an instance of the Flask class to be used for request routing

app = Flask(__name__)

## configuration of database
app.config['SECRET_KEY'] = '' # secret key for sessions (signed cookies). Flask uses it to protect the contents of the user session against tampering.Include your secret key
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = 'your password' #include your password
app.config["MYSQL_DB"] = 'School_Library_New'
app.config["MYSQL_HOST"] = 'localhost'
app.config["WTF_CSRF_SECRET_KEY"] = ''  ## token for csrf protection of forms. Include you secret key

connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='School_Library_New'
)

from school_lib import routes
