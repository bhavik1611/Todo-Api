from flask import Flask, render_template
from flaskext.mysql import MySQL

mysql = MySQL()

app = Flask(__name__)
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'bhavik'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Qwerty@123'
app.config['MYSQL_DATABASE_DB'] = 'todo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)