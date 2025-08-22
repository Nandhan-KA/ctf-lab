import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ctf_lab.db')
SECRET_KEY = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            flag TEXT NOT NULL,
            submitted_flag TEXT,
            score INTEGER DEFAULT 0,
            timestamp TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.before_first_request
def init():
    ensure_schema()


@app.route('/', methods=['GET'])
def index():
    # Single page with Register and Login forms
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()

    if not name or not email:
        flash('Name and Email are required.', 'error')
        return redirect(url_for('index'))

    conn = get_db()
    cur = conn.execute('SELECT * FROM students WHERE email = ?', (email,))
    row = cur.fetchone()

    if row is None:
        # In this lab, students must be preloaded via setup.sh from students.txt
        conn.close()
        flash('Email not found. Please contact your instructor to be added to the exam roster.', 'error')
        return redirect(url_for('index'))

    # Update name if changed
    if row['name'] != name:
        conn.execute('UPDATE students SET name=? WHERE id=?', (name, row['id']))
        conn.commit()

    conn.close()

    session['student_id'] = row['id']
    session['student_name'] = name
    session['student_email'] = email
    return redirect(url_for('submit'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email_login', '').strip().lower()

    if not email:
        flash('Email is required.', 'error')
        return redirect(url_for('index'))

    conn = get_db()
    cur = conn.execute('SELECT * FROM students WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        flash('Account not found. Please register (if in roster) or contact instructor.', 'error')
        return redirect(url_for('index'))

    session['student_id'] = row['id']
    session['student_name'] = row['name']
    session['student_email'] = row['email']
    return redirect(url_for('submit'))


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'student_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('index'))

    student_id = session['student_id']

    conn = get_db()
    row = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if request.method == 'POST':
        submitted = request.form.get('flag', '').strip()
        if not submitted:
            flash('Please enter a flag.', 'error')
            conn.close()
            return redirect(url_for('submit'))

        # Compare
        correct = (submitted == row['flag'])
        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'UPDATE students SET submitted_flag=?, score=?, timestamp=? WHERE id=?',
            (submitted, 1 if correct else 0, ts, student_id)
        )
        conn.commit()
        conn.close()

        if correct:
            return render_template('success.html', name=row['name'], email=row['email'])
        else:
            return render_template('fail.html')

    # GET
    # Provide the student their numeric ID so they know which file to fetch (flag_<id>.txt)
    info = {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        # Do NOT leak the flag here; students must retrieve it via services.
    }

    conn.close()
    return render_template('submit.html', info=info)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Dev server (not for production)
    app.run(host='0.0.0.0', port=5000, debug=True)
