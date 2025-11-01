from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="appuser",
    password="Krishna@2662001",
    database="login_system"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and result['password'] == password:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid username or password!"})




@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if username exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"success": False, "error": "Username already exists!"})

    # Generate registration number
    now = datetime.now()
    year_month = now.strftime("%Y%m")  # e.g., 202511

    # Count users registered this month
    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM users WHERE DATE_FORMAT(registration_date, '%Y%m')=%s",
        (year_month,)
    )
    row = cursor.fetchone()
    count = row['cnt'] if row else 0
    seq_str = str(count + 1).zfill(2)
    registration_number = f"{year_month}{seq_str}"  # e.g. 20251101

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password, registration_date, registration_number) VALUES (%s, %s, NOW(), %s)",
        (username, password, registration_number)
    )
    db.commit()

    return jsonify({"success": True, "registration_number": registration_number})


@app.route('/push', methods=['POST'])
def push_event():
    data = request.json
    username = data.get('username')
    punch_time = datetime.now()

    cursor.execute("INSERT INTO punch_logs (username, punch_time) VALUES (%s, %s)", (username, punch_time))
    db.commit()
    return jsonify({"success": True, "message": f"Punched by {username} at {punch_time}"})


# ADMIN ROUTE: first & last punch per user per date
@app.route('/admin-data', methods=['GET'])
def admin_data():
    query = """
        SELECT 
            username,
            DATE(punch_time) AS date,
            MIN(punch_time) AS first_punch,
            MAX(punch_time) AS last_punch
        FROM punch_logs
        GROUP BY username, DATE(punch_time)
        ORDER BY DATE(punch_time) DESC, username;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    return jsonify({"success": True, "data": data})

# All users punch history
@app.route('/admin-all-data', methods=['GET'])
def admin_all_data():
    query = """
        SELECT 
            u.username,
            DATE(p.punch_time) AS date,
            MIN(p.punch_time) AS first_punch,
            MAX(p.punch_time) AS last_punch
        FROM users u
        LEFT JOIN punch_logs p ON u.username = p.username
        GROUP BY u.username, DATE(p.punch_time)
        ORDER BY u.username, DATE(p.punch_time) DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    data = []
    for r in rows:
        # Access using dictionary keys
        username = r['username']
        date_str = r['date'] if r['date'] else ""
        first_time = r['first_punch'].strftime("%H:%M:%S") if r['first_punch'] else ""
        last_time = r['last_punch'].strftime("%H:%M:%S") if r['last_punch'] else ""

        data.append({
            "username": username,
            "date": date_str,
            "first_punch": first_time,
            "last_punch": last_time
        })

    return jsonify({"success": True, "data": data})

    query = """
        SELECT 
            u.username,
            DATE(p.punch_time) AS date,
            MIN(p.punch_time) AS first_punch,
            MAX(p.punch_time) AS last_punch
        FROM punch_logs u
        LEFT JOIN punch_logs p ON u.username = p.username
        GROUP BY u.username, DATE(p.punch_time)
        ORDER BY u.username, DATE(p.punch_time) DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    data = []
    for r in rows:
        username = r[0]
        date_str = str(r[1]) if r[1] else ""
        first_time = r[2].strftime("%H:%M:%S") if hasattr(r[2], "strftime") and r[2] else ""
        last_time = r[3].strftime("%H:%M:%S") if hasattr(r[3], "strftime") and r[3] else ""
        data.append({
            "username": username,
            "date": date_str,
            "first_punch": first_time,
            "last_punch": last_time
        })
    return jsonify({"success": True, "data": data})


# All users with registration date
@app.route('/admin-users', methods=['GET'])
def admin_users():
    # Include registration_number in SELECT
    query = "SELECT username, registration_date, registration_number FROM users ORDER BY registration_date DESC;"
    cursor.execute(query)
    rows = cursor.fetchall()

    data = []
    for r in rows:
        # Access safely depending on tuple or dict cursor
        username = r[0] if isinstance(r, tuple) else r.get('username')
        reg_date = r[1] if isinstance(r, tuple) else r.get('registration_date')
        reg_no = r[2] if isinstance(r, tuple) else r.get('registration_number')

        # Format registration date
        reg_date_str = reg_date.strftime("%Y-%m-%d") if hasattr(reg_date, "strftime") and reg_date else ""

        data.append({
            "username": username,
            "registration_date": reg_date_str,
            "registration_number": reg_no
        })

    return jsonify({"success": True, "data": data})





if __name__ == "__main__":
    app.run(debug=True)
















# pip install mysql-connector-python
# pip install flask 


#sudo systemctl start mysql
#sudo mysql -u appuser -p


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


# INSERT INTO users (username, password) VALUES ('admin', '123 or hash code of 1234 because we use bcrypt to make hash, ');  ## this is manual method  through registeration page it stire in DB automatically in hash code
#FROM SELECT * FROM appuser;

# SELECT user, host FROM mysql.user;   to see all users in Mysql


# SHOW DATABASES;  to see all the databases of an user

# USE login_system;
# SHOW TABLES;              to see all tables of a database

# DESCRIBE users;     Show Table Structure (Columns and Data Types)

# SELECT * FROM users;      See All Contents of a Table

# SELECT * FROM users LIMIT 10;   You can also limit the number of rows:
