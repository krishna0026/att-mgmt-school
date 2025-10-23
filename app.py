from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="appuser",              # your MySQL username
    password="Krishna@2662001",  # your MySQL password
    database="login_system"      # your database name
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

# 🔹 LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0]
        if password == stored_password:
            return jsonify({"success": True, "username": username})
    return jsonify({"success": False, "error": "Invalid username or password!"})

# 🔹 REGISTER
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"success": False, "error": "Username already exists!"})

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    return jsonify({"success": True})

# 🔹 PUNCH (button press)
@app.route('/push', methods=['POST'])
def push_event():
    data = request.json
    username = data.get('username')

    cursor.execute("INSERT INTO punch_logs (username, punch_time) VALUES (%s, %s)", (username, datetime.now()))
    db.commit()
    return jsonify({"success": True, "message": f"Punched by {username}"})

# 🔹 ADMIN PANEL DATA
@app.route('/admin-data', methods=['GET'])
def admin_data():
    username = request.args.get('username')
    if username != 'admin':  # only admin can access
        return jsonify({"success": False, "error": "Access denied"})
    
    cursor.execute("SELECT username, punch_time FROM punch_logs ORDER BY punch_time DESC")
    rows = cursor.fetchall()
    
    data = [{"username": u, "punch_time": str(t)} for u, t in rows]
    return jsonify({"success": True, "data": data})

if __name__ == "__main__":
    app.run(debug=True)
