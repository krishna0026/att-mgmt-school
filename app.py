from flask import Flask, request, jsonify, render_template
import mysql.connector
import bcrypt
from datetime import datetime

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="appuser",        #  MySQL user
    password="Krishna@2662001",#  MySQL password
    database="login_system"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    query = "SELECT password FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0]
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid username or password!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"success": False, "error": "Username already exists!"})
    
      # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    db.commit()
    return jsonify({"success": True})

# New route: Log push events
@app.route('/push', methods=['POST'])
def push_event():
    data = request.json
    username = data.get('username')

    cursor.execute("INSERT INTO punch_logs (username) VALUES (%s)", (username,))
    db.commit()

    return jsonify({"success": True, "message": f"Punched by {username} at {datetime.now()}"})


if __name__ == "__main__":
    app.run(debug=True)



# pip install mysql-connector-python
# pip install flask 



# CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'Krishna@2662001';
# GRANT ALL PRIVILEGES ON login_system.* TO 'appuser'@'localhost';
# FLUSH PRIVILEGES;

# CREATE DATABASE login_system;
# USE login_system;


# CREATE TABLE users (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(50) NOT NULL UNIQUE,
#     password VARCHAR(255) NOT NULL
# );


# INSERT INTO users (username, password) VALUES ('admin', '1234 or hash code of 1234 because we use bcrypt to make hash, ');  ## this is manual method  through registeration page it stire in DB automatically in hash code
#FROM SELECT * FROM appuser;

# SELECT user, host FROM mysql.user;   to see all users in Mysql


# SHOW DATABASES;  to see all the databases of an user

# USE login_system;
# SHOW TABLES;              to see all tables of a database

# DESCRIBE users;     Show Table Structure (Columns and Data Types)

# SELECT * FROM users;      See All Contents of a Table

# SELECT * FROM users LIMIT 10;   You can also limit the number of rows:





