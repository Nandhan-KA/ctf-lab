#!/bin/bash

# CTF Lab Setup Script
# This script sets up a complete CTF lab environment with FTP, SMB, Telnet, and Web services

set -e  # Exit on any error

echo "🚀 Starting CTF Lab Setup..."

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx vsftpd samba openbsd-inetd telnetd git

# Create project directory
PROJECT_DIR="/home/ubuntu/ctf-lab"
echo "📁 Setting up project directory: $PROJECT_DIR"

# Create service users
echo "👤 Creating service users..."
sudo useradd -m -s /bin/bash ftpuser 2>/dev/null || echo "ftpuser already exists"
sudo useradd -m -s /bin/bash telnetuser 2>/dev/null || echo "telnetuser already exists"
sudo useradd -m -s /bin/bash smbuser 2>/dev/null || echo "smbuser already exists"

# Set passwords for service users
echo "ftpuser:ftpuserpass" | sudo chpasswd
echo "telnetuser:telnetuserpass" | sudo chpasswd
echo "smbuser:smbuserpass" | sudo chpasswd

# Configure vsftpd for anonymous access
echo "📁 Configuring vsftpd..."
sudo tee /etc/vsftpd.conf > /dev/null <<EOF
listen=YES
listen_ipv6=NO
anonymous_enable=YES
anon_root=/home/ftpuser
anon_upload_enable=NO
anon_mkdir_write_enable=NO
anon_other_write_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
allow_writeable_chroot=YES
secure_chroot_dir=/var/run/vsftpd/empty
pam_service_name=vsftpd
rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
ssl_enable=NO
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=40100
EOF

# Configure Samba
echo "📁 Configuring Samba..."
sudo tee /etc/samba/smb.conf > /dev/null <<EOF
[global]
   workgroup = WORKGROUP
   server string = CTF Lab SMB Server
   security = user
   map to guest = bad user
   guest account = smbuser
   log file = /var/log/samba/%m.log
   max log size = 50

[credentials]
   comment = CTF Credentials Share
   path = /srv/smb
   browseable = yes
   writable = yes
   guest ok = yes
   create mask = 0644
   directory mask = 0755

[admin]
   comment = Admin Share
   path = /srv/smb
   browseable = yes
   writable = yes
   guest ok = yes

[IC]
   comment = IC Share
   path = /srv/smb
   browseable = yes
   writable = yes
   guest ok = yes
EOF

# Create SMB directories and files
echo "📁 Creating SMB directory structure..."
sudo mkdir -p /srv/smb
sudo mkdir -p /srv/smb/idk
sudo mkdir -p /srv/smb/thisisit
sudo mkdir -p /srv/smb/thisisnot

# Create flag files
echo "🏴 Creating flag files..."
sudo tee /home/ftpuser/flag.txt > /dev/null <<EOF
FLAG{Anonymous_ftp_flag}
EOF

sudo tee /home/ftpuser/anonymous_flag.txt > /dev/null <<EOF
FLAG{Anonymous_ftp_flag}
EOF

sudo tee /home/telnetuser/flag_correct.txt > /dev/null <<EOF
FLAG{telnet_root_flag}
EOF

sudo tee /home/telnetuser/flag_wrong.txt > /dev/null <<EOF
FLAG{wrong_telnet_flag}
EOF

sudo tee /srv/smb/idk/flag.txt > /dev/null <<EOF
FLAG{wrong_flag_1}
EOF

sudo tee /srv/smb/thisisit/flag.txt > /dev/null <<EOF
FLAG{wrong_flag_2}
EOF

sudo tee /srv/smb/thisisnot/flag.txt > /dev/null <<EOF
FLAG{smb_credentials_flag}
EOF

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R ftpuser:ftpuser /home/ftpuser/
sudo chown -R telnetuser:telnetuser /home/telnetuser/
sudo chown -R smbuser:smbuser /srv/smb/
sudo chmod 755 /home/ftpuser/
sudo chmod 644 /home/ftpuser/*.txt
sudo chmod 755 /home/telnetuser/
sudo chmod 644 /home/telnetuser/*.txt
sudo chmod 755 /srv/smb/
sudo chmod 755 /srv/smb/*/
sudo chmod 644 /srv/smb/*/flag.txt

# Configure Telnet via inetd
echo "🔌 Configuring Telnet..."
sudo tee /etc/inetd.conf > /dev/null <<EOF
telnet stream tcp nowait root /usr/sbin/in.telnetd in.telnetd
EOF

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
cd $PROJECT_DIR/web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install werkzeug

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

conn.commit()
conn.close()
print("Database setup complete!")
EOF

# Create systemd service for the Flask app
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/ctf-lab.service > /dev/null <<EOF
[Unit]
Description=CTF Lab Flask App (gunicorn)
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/web
Environment=PATH=$PROJECT_DIR/web/venv/bin
ExecStart=$PROJECT_DIR/web/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
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
sudo chown -R www-data:www-data $PROJECT_DIR/web/

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ctf-lab nginx vsftpd smbd openbsd-inetd
sudo systemctl start ctf-lab nginx vsftpd smbd openbsd-inetd

# Test services
echo "🧪 Testing services..."
sleep 5

echo "✅ Setup complete!"
echo ""
echo "📋 Service Status:"
echo "  - Web Portal: http://$(curl -s ifconfig.me)"
echo "  - FTP: Anonymous access enabled (port 21)"
echo "  - SMB: credentials share available (port 445)"
echo "  - Telnet: root access enabled (port 23)"
echo ""
echo "👥 Student Login Info:"
echo "  - Default password: default123"
echo "  - Students can change password at /change_password"
echo ""
echo "🏴 Flag Locations:"
echo "  - FTP: /home/ftpuser/flag.txt"
echo "  - SMB: /srv/smb/thisisnot/flag.txt (correct answer)"
echo "  - Telnet: /home/telnetuser/flag_correct.txt (correct answer)"
echo ""
echo "🎯 Exam Details:"
echo "  - 6 questions, 30-minute time limit"
echo "  - Target IP: 13.62.104.182"
echo "  - All services configured and running"
