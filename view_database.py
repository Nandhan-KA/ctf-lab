#!/usr/bin/env python3
"""
Database Viewer for CTF Lab
Instructors can use this to view student data and submissions
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    """View the contents of the CTF Lab database"""
    db_path = "web/ctf_lab.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Run setup.sh first to create the database")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("CTF LAB DATABASE VIEWER")
    print("=" * 60)
    
    # View students
    print("\n📚 STUDENTS TABLE:")
    print("-" * 40)
    cursor.execute("SELECT * FROM students ORDER BY id")
    students = cursor.fetchall()
    
    if not students:
        print("No students found in database")
    else:
        for student in students:
            status = "Not Registered" if student['registered'] == 0 else "Pre-registered" if student['registered'] == 1 else "Fully Registered"
            print(f"ID: {student['id']}")
            print(f"  Name: {student['name']}")
            print(f"  Email: {student['email']}")
            print(f"  Register #: {student['register_number']}")
            print(f"  Year/Dept: {student['year_dept']}")
            print(f"  Phone: {student['phone_number']}")
            print(f"  Status: {status}")
            print(f"  Flag: {student['flag']}")
            if student['login_time']:
                print(f"  Login Time: {student['login_time']}")
            if student['time_limit']:
                print(f"  Time Limit: {student['time_limit']}")
            print()
    
    # View submissions
    print("\n📝 SUBMISSIONS TABLE:")
    print("-" * 40)
    cursor.execute("SELECT s.*, st.name FROM submissions s JOIN students st ON s.student_id = st.id ORDER BY s.submitted_at DESC")
    submissions = cursor.fetchall()
    
    if not submissions:
        print("No submissions found in database")
    else:
        for submission in submissions:
            print(f"Submission ID: {submission['id']}")
            print(f"  Student: {submission['name']} (ID: {submission['student_id']})")
            print(f"  Score: {submission['score']}/6")
            print(f"  Submitted: {submission['submitted_at']}")
            print(f"  Q1 (Services): {submission['question_1']}")
            print(f"  Q2 (FTP Flag): {submission['question_2']}")
            print(f"  Q3 (SMB Flag): {submission['question_3']}")
            print(f"  Q4 (Telnet Flag): {submission['question_4']}")
            print(f"  Q5 (Versions): {submission['question_5']}")
            print(f"  Q6 (OS): {submission['question_6']}")
            print()
    
    # Summary statistics
    print("\n📊 SUMMARY STATISTICS:")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total_students = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM students WHERE registered > 0")
    registered_students = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM submissions")
    total_submissions = cursor.fetchone()['total']
    
    if total_submissions > 0:
        cursor.execute("SELECT AVG(score) as avg_score FROM submissions")
        avg_score = cursor.fetchone()['avg_score']
        
        cursor.execute("SELECT COUNT(*) as perfect FROM submissions WHERE score = 6")
        perfect_scores = cursor.fetchone()['perfect']
        
        print(f"Total Students: {total_students}")
        print(f"Registered Students: {registered_students}")
        print(f"Total Submissions: {total_submissions}")
        print(f"Average Score: {avg_score:.2f}/6")
        print(f"Perfect Scores (6/6): {perfect_scores}")
    else:
        print(f"Total Students: {total_students}")
        print(f"Registered Students: {registered_students}")
        print("No submissions yet")
    
    conn.close()

if __name__ == "__main__":
    try:
        view_database()
    except Exception as e:
        print(f"Error viewing database: {e}")
        import traceback
        traceback.print_exc()
