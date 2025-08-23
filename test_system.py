#!/usr/bin/env python3
"""
Test script for CTF Lab Simulation System
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

def test_database():
    """Test database connectivity and schema"""
    print("🧪 Testing database...")
    
    db_path = os.path.join('web', 'ctf_lab.db')
    if not os.path.exists(db_path):
        print("❌ Database not found. Run setup.sh first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test students table
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"✅ Students table: {student_count} students found")
        
        # Test submissions table
        cursor.execute("SELECT COUNT(*) FROM submissions")
        submission_count = cursor.fetchone()[0]
        print(f"✅ Submissions table: {submission_count} submissions found")
        
        # Test sample student
        cursor.execute("SELECT roll_number, name FROM students LIMIT 1")
        student = cursor.fetchone()
        if student:
            print(f"✅ Sample student: {student[0]} - {student[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("\n🔐 Testing password hashing...")
    
    test_password = "test123"
    hashed = generate_password_hash(test_password)
    
    if check_password_hash(hashed, test_password):
        print("✅ Password hashing works correctly")
        return True
    else:
        print("❌ Password hashing failed")
        return False

def test_flask_app():
    """Test Flask app imports"""
    print("\n🌐 Testing Flask app...")
    
    try:
        import sys
        sys.path.append('web')
        from app import app, get_db_connection, ensure_schema
        
        print("✅ Flask app imports successfully")
        
        # Test database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection works")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_students_file():
    """Test students.txt file"""
    print("\n📋 Testing students.txt...")
    
    if not os.path.exists('students.txt'):
        print("❌ students.txt not found")
        return False
    
    try:
        with open('students.txt', 'r') as f:
            lines = f.readlines()
        
        student_count = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    student_count += 1
        
        print(f"✅ students.txt: {student_count} students found")
        return True
        
    except Exception as e:
        print(f"❌ students.txt test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CTF Lab Simulation System Test")
    print("=" * 40)
    
    tests = [
        test_students_file,
        test_database,
        test_password_hashing,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\n📝 To start the system:")
        print("  cd web")
        print("  source venv/bin/activate")
        print("  python app.py")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the setup.")
        print("\n💡 Try running: ./setup.sh")

if __name__ == "__main__":
    main()
