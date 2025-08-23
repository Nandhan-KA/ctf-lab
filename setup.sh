#!/bin/bash

# CTF Lab Setup Script - Simulation-Based System
# This script sets up a web-based CTF lab simulation environment

set -e  # Exit on any error

echo "🚀 Starting CTF Lab Simulation Setup..."

# Check if we're in the right directory
if [ ! -f "web/app.py" ]; then
    echo "❌ Error: Please run this script from the ctf-lab directory"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx git

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
cd web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create database and populate with student data
echo "🗄️ Setting up database..."
python3 <<EOF
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Create database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctf_lab.db')
conn = sqlite3.connect(db_path)
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

# Read students from file and insert into database
students_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'students.txt')
default_password = generate_password_hash('default123')

if os.path.exists(students_file):
    with open(students_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    roll_number = parts[0].strip()
                    name = parts[1].strip()
                    
                    # Insert or update student
                    cursor.execute('''
                        INSERT OR REPLACE INTO students (roll_number, name, password, registered)
                        VALUES (?, ?, ?, 1)
                    ''', (roll_number, name, default_password))
    print(f"Added students from {students_file}")
else:
    print(f"Warning: {students_file} not found. No students added to database.")

conn.commit()
conn.close()
print("Database setup complete!")
EOF

# Create systemd service for the Flask app (optional)
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/ctf-lab.service > /dev/null <<EOF
[Unit]
Description=CTF Lab Simulation Flask App
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx (optional)
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/ctf-lab > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/ctf-lab /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Set proper ownership for web files
sudo chown -R www-data:www-data $(pwd)/

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ctf-lab nginx
sudo systemctl start ctf-lab nginx

# Test the application
echo "🧪 Testing application..."
sleep 3

echo "✅ Setup complete!"
echo ""
echo "📋 Application Information:"
echo "  - Web Portal: http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost')"
echo "  - Local Access: http://localhost:5000"
echo ""
echo "👥 Student Login Info:"
echo "  - Default password: default123"
echo "  - Students can change password at /change_password"
echo ""
echo "🎯 Simulation Features:"
echo "  - Web-based terminal emulator"
echo "  - Simulated FTP, SMB, Telnet services"
echo "  - Pre-configured flags and responses"
echo "  - 30-minute exam timer"
echo ""
echo "🏴 Available Flags:"
echo "  - FTP: FLAG{Anonymous_ftp_flag}"
echo "  - SMB: FLAG{smb_credentials_flag}"
echo "  - Telnet: FLAG{telnet_root_flag}"
echo ""
echo "🎮 Available Commands:"
echo "  - nmap 13.62.104.182"
echo "  - ftp 13.62.104.182"
echo "  - smbclient //13.62.104.182/credentials"
echo "  - telnet 13.62.104.182"
echo ""
echo "📝 To start manually:"
echo "  cd web"
echo "  source venv/bin/activate"
echo "  python app.py"
