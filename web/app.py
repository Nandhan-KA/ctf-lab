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

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctf_lab.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_flags(roll_number):
    """Generate unique flags for a student based on their roll number"""
    import hashlib
    hash_base = hashlib.md5(roll_number.encode()).hexdigest()[:8]
    
    return {
        'ftp_flag': f'FLAG{{ftp_{hash_base}_flag}}',
        'smb_flag': f'FLAG{{smb_{hash_base}_flag}}',
        'telnet_flag': f'FLAG{{telnet_{hash_base}_flag}}'
    }

def ensure_schema():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                flag TEXT,
                registered INTEGER DEFAULT 1,
                login_time DATETIME,
                time_limit DATETIME
            )
        ''')
        
        # Create submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                roll_number TEXT,
                name TEXT,
                q1_answer TEXT,
                q2_answer TEXT,
                q3_answer TEXT,
                q4_answer TEXT,
                q5_answer TEXT,
                q6_answer TEXT,
                score INTEGER,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        conn.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
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
                result = cursor.fetchone()
                if result and result['time_limit']:
                    time_limit = datetime.fromisoformat(result['time_limit'])
                    if datetime.now() > time_limit:
                        return redirect(url_for('time_expired'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    roll_number = request.form.get('roll_number')
    password = request.form.get('password')
    
    if not roll_number or not password:
        flash('Please enter both roll number and password')
        return redirect(url_for('index'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE roll_number = ?', (roll_number,))
        student = cursor.fetchone()
        
        if student and check_password_hash(student['password'], password):
            session['student_id'] = student['id']
            session['roll_number'] = student['roll_number']
            session['name'] = student['name']
            
            # Set login time and time limit (30 minutes)
            login_time = datetime.now()
            time_limit = login_time + timedelta(minutes=30)
            
            cursor.execute('''
                UPDATE students 
                SET login_time = ?, time_limit = ? 
                WHERE id = ?
            ''', (login_time.isoformat(), time_limit.isoformat(), student['id']))
            conn.commit()
            
            session['login_time'] = login_time.isoformat()
            session['time_limit'] = time_limit.isoformat()
            
            return redirect(url_for('terminal'))
        else:
            flash('Invalid roll number or password')
            return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not roll_number or not new_password or not confirm_password:
            flash('Please fill all fields')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match')
            return render_template('change_password.html')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE roll_number = ?', (roll_number,))
            student = cursor.fetchone()
            
            if student:
                hashed_password = generate_password_hash(new_password)
                cursor.execute('''
                    UPDATE students 
                    SET password = ?, registered = 2 
                    WHERE roll_number = ?
                ''', (hashed_password, roll_number))
                conn.commit()
                flash('Password changed successfully! You can now login.')
                return redirect(url_for('index'))
            else:
                flash('Roll number not found')
                return render_template('change_password.html')
    
    return render_template('change_password.html')

@app.route('/terminal')
@login_required
@check_time_limit
def terminal():
    # Generate dynamic flags based on student's roll number
    roll_number = session.get('roll_number', '')
    flags = generate_flags(roll_number)
    
    return render_template('terminal.html', flags=flags)

@app.route('/submit_answers', methods=['GET', 'POST'])
@login_required
@check_time_limit
def submit_answers():
    if request.method == 'POST':
        # Get answers from form
        q1_answer = request.form.get('q1', '').strip()
        q2_answer = request.form.get('q2', '').strip()
        q3_answer = request.form.get('q3', '').strip()
        q4_answer = request.form.get('q4', '').strip()
        q5_answer = request.form.get('q5', '').strip()
        q6_answer = request.form.get('q6', '').strip()
        
        # Generate dynamic correct answers based on student's roll number
        roll_number = session.get('roll_number', '')
        flags = generate_flags(roll_number)
        
        correct_answers = {
            'q1': '21/tcp open ftp vsftpd 2.0.8 or later, 22/tcp open ssh OpenSSH 8.9p1 Ubuntu 3ubuntu0.13, 23/tcp open telnet, 80/tcp open http nginx 1.18.0',
            'q2': flags['ftp_flag'],
            'q3': flags['smb_flag'],
            'q4': flags['telnet_flag'],
            'q5': 'vsftpd 2.0.8 or later, Samba 4.15.9, telnetd',
            'q6': 'Linux'
        }
        
        # Calculate score
        score = 0
        for q_num, correct_answer in correct_answers.items():
            if q_num == 'q1':
                # For Q1, check if all required services are mentioned
                student_answer = q1_answer.lower()
                required_services = ['ftp', 'ssh', 'telnet', 'http']
                if all(service in student_answer for service in required_services):
                    score += 1
            elif q_num == 'q2' and q2_answer == correct_answer:
                score += 1
            elif q_num == 'q3' and q3_answer == correct_answer:
                score += 1
            elif q_num == 'q4' and q4_answer == correct_answer:
                score += 1
            elif q_num == 'q5' and q5_answer == correct_answer:
                score += 1
            elif q_num == 'q6' and q6_answer.lower() == correct_answer.lower():
                score += 1
        
        # Save submission to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO submissions 
                (student_id, roll_number, name, q1_answer, q2_answer, q3_answer, q4_answer, q5_answer, q6_answer, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['student_id'], session['roll_number'], session['name'],
                q1_answer, q2_answer, q3_answer, q4_answer, q5_answer, q6_answer, score
            ))
            conn.commit()
        
        return redirect(url_for('results'))
    
    return render_template('submit.html')

@app.route('/results')
@login_required
def results():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM submissions 
            WHERE student_id = ? 
            ORDER BY submitted_at DESC 
            LIMIT 1
        ''', (session['student_id'],))
        submission = cursor.fetchone()
        
        if submission:
            return render_template('results.html', submission=submission)
        else:
            return redirect(url_for('submit_answers'))

@app.route('/time_expired')
def time_expired():
    return render_template('time_expired.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/time_remaining')
@login_required
def time_remaining():
    if 'time_limit' in session:
        time_limit = datetime.fromisoformat(session['time_limit'])
        remaining = time_limit - datetime.now()
        if remaining.total_seconds() <= 0:
            return jsonify({'expired': True})
        return jsonify({
            'expired': False,
            'remaining_seconds': int(remaining.total_seconds())
        })
    return jsonify({'expired': True})

if __name__ == '__main__':
    ensure_schema()
    app.run(debug=True, host='0.0.0.0', port=5001)