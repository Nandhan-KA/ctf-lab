# ctf-lab/web/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
from datetime import datetime, timedelta
import time

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# Database initialization
def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctf_lab.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                register_number TEXT UNIQUE NOT NULL,
                year_dept TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                password TEXT NOT NULL,
                flag TEXT NOT NULL,
                registered INTEGER DEFAULT 0,
                login_time TIMESTAMP,
                time_limit TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                question_1 TEXT,
                question_2 TEXT,
                question_3 TEXT,
                question_4 TEXT,
                question_5 TEXT,
                question_6 TEXT,
                score INTEGER DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            );
        ''')
        conn.commit()

# Initialize database on startup
with app.app_context():
    ensure_schema()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def check_time_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' in session:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT time_limit FROM students WHERE id = ?', (session['student_id'],))
                student = cursor.fetchone()
                if student and student['time_limit']:
                    time_limit = datetime.fromisoformat(student['time_limit'])
                    if datetime.now() > time_limit:
                        flash('Time limit exceeded! You cannot submit answers anymore.', 'danger')
                        return redirect(url_for('time_expired'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    register_number = request.form.get('register_number')
    year_dept = request.form.get('year_dept')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    
    if not all([name, email, register_number, year_dept, phone_number, password]):
        flash('All fields are required!', 'danger')
        return redirect(url_for('index'))
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM students WHERE email = ? OR register_number = ?', (email, register_number))
            if cursor.fetchone():
                flash('Email or Register Number already registered!', 'danger')
                return redirect(url_for('index'))
            
            hashed_password = generate_password_hash(password)
            flag = f'FLAG_{name.replace(" ", "")}_{os.urandom(8).hex()}'
            cursor.execute(
                'INSERT INTO students (name, email, register_number, year_dept, phone_number, password, flag, registered) VALUES (?, ?, ?, ?, ?, ?, ?, 1)',
                (name, email, register_number, year_dept, phone_number, hashed_password, flag)
            )
            student_id = cursor.lastrowid
            conn.commit()
            
            session['student_id'] = student_id
            session['student_name'] = name
            flash('Registration successful! Please login to start the exam.', 'success')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error during registration: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not all([email, password]):
        flash('Email and password are required!', 'danger')
        return redirect(url_for('index'))
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, password, registered FROM students WHERE email = ?', (email,))
            student = cursor.fetchone()
            
            if student and check_password_hash(student['password'], password):
                # Check if this is a pre-registered student who needs to set their own password
                if student['registered'] == 1:
                    # Set login time and 30-minute limit
                    login_time = datetime.now()
                    time_limit = login_time + timedelta(minutes=30)
                    
                    cursor.execute(
                        'UPDATE students SET login_time = ?, time_limit = ? WHERE id = ?',
                        (login_time.isoformat(), time_limit.isoformat(), student['id'])
                    )
                    conn.commit()
                    
                    session['student_id'] = student['id']
                    session['student_name'] = student['name']
                    session['login_time'] = login_time.isoformat()
                    session['time_limit'] = time_limit.isoformat()
                    
                    flash('Login successful! You have 30 minutes to complete the exam.', 'success')
                    return redirect(url_for('submit_answers'))
                else:
                    flash('Please complete your registration first.', 'warning')
                    return redirect(url_for('index'))
            else:
                flash('Invalid email or password!', 'danger')
                return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error during login: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([email, current_password, new_password, confirm_password]):
            flash('All fields are required!', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return render_template('change_password.html')
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, password FROM students WHERE email = ?', (email,))
                student = cursor.fetchone()
                
                if student and check_password_hash(student['password'], current_password):
                    # Update password and mark as fully registered
                    hashed_password = generate_password_hash(new_password)
                    cursor.execute(
                        'UPDATE students SET password = ?, registered = 2 WHERE id = ?',
                        (hashed_password, student['id'])
                    )
                    conn.commit()
                    
                    flash('Password changed successfully! You can now login with your new password.', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or current password!', 'danger')
        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'danger')
    
    return render_template('change_password.html')

@app.route('/submit', methods=['GET', 'POST'])
@login_required
@check_time_limit
def submit_answers():
    if request.method == 'POST':
        q1 = request.form.get('question_1', '').strip()
        q2 = request.form.get('question_2', '').strip()
        q3 = request.form.get('question_3', '').strip()
        q4 = request.form.get('question_4', '').strip()
        q5 = request.form.get('question_5', '').strip()
        q6 = request.form.get('question_6', '').strip()
        
        if not all([q1, q2, q3, q4, q5, q6]):
            flash('Please answer all questions!', 'danger')
            return render_template('submit.html')
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if already submitted
                cursor.execute('SELECT id FROM submissions WHERE student_id = ?', (session['student_id'],))
                if cursor.fetchone():
                    flash('You have already submitted answers!', 'warning')
                    return redirect(url_for('view_results'))
                
                # Calculate score
                score = 0
                correct_answers = {
                    'question_1': 'ftp, ssh, http, telnet',  # Services running
                    'question_2': 'FLAG{Anonymous_ftp_flag}',  # FTP flag
                    'question_3': 'FLAG{smb_credentials_flag}',  # SMB flag from thisisnot folder
                    'question_4': 'FLAG{telnet_root_flag}',  # Telnet flag (correct one)
                    'question_5': 'vsftpd 2.0.8 or later, SMB version info, telnet closed',  # Service versions
                    'question_6': 'Linux'  # Operating system
                }
                
                if q1.lower() in correct_answers['question_1'].lower():
                    score += 1
                if q2.lower() in correct_answers['question_2'].lower():
                    score += 1
                if q3.lower() in correct_answers['question_3'].lower():
                    score += 1
                if q4.lower() in correct_answers['question_4'].lower():
                    score += 1
                if q5.lower() in correct_answers['question_5'].lower():
                    score += 1
                if q6.lower() in correct_answers['question_6'].lower():
                    score += 1
                
                cursor.execute(
                    'INSERT INTO submissions (student_id, question_1, question_2, question_3, question_4, question_5, question_6, score) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (session['student_id'], q1, q2, q3, q4, q5, q6, score)
                )
                conn.commit()
                
                flash(f'Answers submitted successfully! Your score: {score}/6', 'success')
                return redirect(url_for('view_results'))
                
        except Exception as e:
            flash(f'Error submitting answers: {str(e)}', 'danger')
    
    return render_template('submit.html')

@app.route('/results')
@login_required
def view_results():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM submissions WHERE student_id = ?', (session['student_id'],))
            submission = cursor.fetchone()
            
            if not submission:
                flash('No submission found. Please submit your answers first.', 'warning')
                return redirect(url_for('submit_answers'))
            
            return render_template('results.html', submission=submission)
    except Exception as e:
        flash(f'Error retrieving results: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/time_expired')
def time_expired():
    return render_template('time_expired.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/api/time_remaining')
@login_required
def time_remaining():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT time_limit FROM students WHERE id = ?', (session['student_id'],))
            student = cursor.fetchone()
            
            if student and student['time_limit']:
                time_limit = datetime.fromisoformat(student['time_limit'])
                remaining = (time_limit - datetime.now()).total_seconds()
                
                if remaining <= 0:
                    return jsonify({'expired': True, 'remaining': 0})
                else:
                    return jsonify({'expired': False, 'remaining': int(remaining)})
            
            return jsonify({'expired': True, 'remaining': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)