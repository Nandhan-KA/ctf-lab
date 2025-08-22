# CTF Exam Lab (Beginner)

A self-contained beginner-friendly CTF lab focused on enumerating FTP, Telnet, and SMB, answering 6 specific questions, and submitting answers via a simple web portal within a 30-minute time limit.

## Features
- Automated setup on Ubuntu (WSL or VPS) via `setup.sh`.
- Services: FTP (`vsftpd` with anonymous access), Telnet (`telnetd` with root access), SMB (Samba with multiple shares).
- Web portal (Flask + Gunicorn + Nginx) for registration/login and exam submission.
- 6-question exam format with automatic scoring.
- 30-minute time limit per student session.
- Per-student unique flags generated from `students.txt` and stored in SQLite.

## Project Structure
```
ctf-lab/
├── setup.sh                  # Installs & configures all services + flags
├── docker-compose.yml        # Optional local web testing
├── services/
│   ├── ftp/
│   │   └── vsftpd.conf
│   ├── telnet/
│   │   └── telnet.xinetd
│   └── smb/
│       └── smb.conf
├── web/
│   ├── app.py                # Flask web app
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── submit.html
│   │   ├── results.html
│   │   └── time_expired.html
│   └── requirements.txt
├── students.txt              # CSV: Name,Email,RegisterNumber,YearDept,PhoneNumber
├── FLAG_PLACEMENT_GUIDE.md  # Detailed guide for flag locations
└── README.md
```

## Prerequisites
- Ubuntu 20.04+ (bare VPS or WSL) with `sudo` privileges and port 80 open (if public).
- DNS or public IP to share with students.

### Firewall / Cloud Security Group
Ensure inbound rules allow these TCP ports from student networks:
- 80 (HTTP, web portal)
- 21 (FTP)
- 23 (Telnet)
- 445 (SMB)

On Ubuntu UFW, for example:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 21/tcp
sudo ufw allow 23/tcp
sudo ufw allow 445/tcp
sudo ufw reload
```

## Quick Start (Ubuntu)
1. Copy the project to your server.
2. Edit `students.txt` to include all students. One per line as `Name,Email`.
3. Run the setup:
   ```bash
   sudo bash setup.sh
   ```
4. After setup:
   - Web portal: `http://<server_public_ip>/`
   - Service configurations:
     - FTP: Anonymous access with password `12345678`
     - Telnet: Root access (no password required)
     - SMB: user `smbuser`, pass `smbuserpass`, shares: `credentials`, `admin`, `IC`

### Note on WSL
If running under WSL, you may need to enable systemd for services (xinetd/inetd, smbd, nginx) to start automatically. See Microsoft docs on enabling systemd in WSL, or run the web app manually:
```bash
cd web
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
# then browse http://localhost:5000
```

## Database Structure

The CTF Lab uses SQLite with the following schema:

### Students Table
```sql
CREATE TABLE students (
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
```

**Field Descriptions:**
- `registered`: 0 = not registered, 1 = pre-registered (needs password change), 2 = fully registered
- `login_time`: When student logged in for exam
- `time_limit`: 30-minute deadline from login

### Submissions Table
```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    question_1 TEXT,  -- Services running
    question_2 TEXT,  -- FTP flag
    question_3 TEXT,  -- SMB flag
    question_4 TEXT,  -- Telnet flag
    question_5 TEXT,  -- Service versions
    question_6 TEXT,  -- Operating system
    score INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id)
);
```

## Instructor Notes
- Flags are generated per student in the format `FLAG{Name_randomHex}`.
- Students have 30 minutes from login to complete the exam.
- The exam consists of 6 questions covering service enumeration and flag retrieval.
- **Database Schema**: The system now uses two tables:
  - `students`: Stores student information, passwords, and session timing
  - `submissions`: Stores exam answers and scores
- **Registration System**: Two registration methods:
  1. **Instructor Pre-registration**: Students added via `students.txt` get default passwords
  2. **Student Self-registration**: Students can register themselves with custom passwords
- **Password Management**: Pre-registered students must change their default passwords before accessing the exam
- Flags are placed here (by student ID in DB):
  - FTP: `/home/ftpuser/flags/flag_<id>.txt`
  - Telnet: `/home/telnetuser/flags/flag_<id>.txt`
  - SMB: `/srv/smb/flags/flag_<id>.txt`
- The web app validates submitted answers against predefined correct answers and stores results in SQLite DB at `web/ctf_lab.db`.

### Add/Update Students
- Edit `students.txt` and re-run `sudo bash setup.sh`. Existing emails will be updated with new flags.
- **Note**: Students added via `students.txt` will have default passwords and need to change them before accessing the exam.

### View Database Contents
To view student data and submissions:
```bash
python3 view_database.py
```
This script shows:
- All registered students and their status
- Exam submissions and scores
- Summary statistics (average scores, perfect scores, etc.)

### Verify Flag Placement
To verify that all required flag files are in place:
```bash
sudo python3 verify_flags.py
```
This script checks:
- All flag files exist and are readable
- SMB folder structure is correct
- Services are running properly
- Per-student flag directories are accessible

### Reset Lab
- To reset flags and scores but keep students:
  ```bash
  sudo systemctl stop ctf-lab
  rm -f web/ctf_lab.db
  sudo bash setup.sh
  ```
- To wipe service flag files:
  ```bash
  sudo rm -f /home/ftpuser/flags/flag_*.txt
  sudo rm -f /home/telnetuser/flags/flag_*.txt
  sudo rm -f /srv/smb/flags/flag_*.txt
  ```
  Then re-run `setup.sh` to regenerate.

## Student Workflow
1. Go to `http://<server_public_ip>/`.
2. Register with: Name, Email, Register Number, Year & Department, Phone Number, Password.
3. Login with your email and password.
4. You will have 30 minutes to complete the exam.
5. Answer all 6 questions based on your investigation of the target server.
6. Submit answers before time expires.

## Exam Questions

### Question 1: Service Enumeration
**What are all the services running on the IP 13.62.104.182?**
- Students must scan the target and identify running services (FTP, SSH, HTTP, Telnet)

### Question 2: FTP Flag
**Flag for FTP (connect using user: Anonymous, pass: 12345678)**
- Students connect anonymously to FTP and retrieve the flag
- **Flag Location:** `/home/ftpuser/flag.txt` contains `FLAG{Anonymous_ftp_flag}`

### Question 3: SMB Flag
**Flag for SMB (use smbclient //13.62.104.182/credentials, check all three folders: idk, thisisit, thisisnot - the flag in thisisnot folder is the answer)**
- Students access SMB shares and navigate through folders to find the correct flag
- **Correct Flag Location:** `/srv/smb/thisisnot/flag.txt` contains `FLAG{smb_credentials_flag}`
- **Wrong Flags:** Other folders contain different flags to test student understanding

### Question 4: Telnet Flag
**Telnet flag (connect using root without password, there are 2 flags - find the correct one)**
- Students connect as root via telnet and identify the correct flag from two options
- **Correct Flag Location:** `/home/telnetuser/flag_correct.txt` contains `FLAG{telnet_root_flag}`

### Question 5: Service Versions
**What is the version of FTP, SMB, and Telnet running on the server 13.62.104.182?**
- Students use version detection tools to identify service versions
- **Expected Answer:** vsftpd 2.0.8 or later, SMB version info, telnet closed

### Question 6: Operating System
**What type of operating system is running on the server?**
- Students identify the OS from service banners and responses
- **Expected Answer:** Linux

## Flag Placement Details

For detailed information about where each flag is placed and how students should access them, see [FLAG_PLACEMENT_GUIDE.md](FLAG_PLACEMENT_GUIDE.md).

This guide includes:
- Exact file paths for each flag
- Student access commands for each service
- Complete folder structure
- Verification commands for instructors

## Example Commands for Students

### Service Enumeration
```bash
# Fast top ports
nmap -sS -Pn -T4 13.62.104.182

# Full TCP port scan
nmap -sS -p- -T4 13.62.104.182

# Service/version detection
nmap -sV -sC -p 21,23,445 13.62.104.182
```

### FTP Access
```bash
ftp 13.62.104.182
# Username: Anonymous
# Password: 12345678
get flag.txt
```

### SMB Access
```bash
smbclient //13.62.104.182/credentials -U smbuser
# Password: smbuserpass
cd idk
ls
cd ../thisisit
ls
cd ../thisisnot
get flag.txt
```

### Telnet Access
```bash
telnet 13.62.104.182
# Login: root
# Password: (none)
cat flag_correct.txt
cat flag_wrong.txt
```

## Local Web App Testing (Optional)
If you only want to test the Flask app locally (without services), use Docker Compose:
```bash
docker compose up --build
# Open http://localhost:5000
```
Note: The compose setup does not run FTP/Telnet/SMB; it only starts the web app.

## Security Notes
- This lab intentionally exposes legacy services (FTP, Telnet) and allows root telnet access. Run it on an isolated VPS or lab network.
- Use firewall rules to restrict access if needed.
- Do not reuse credentials elsewhere.
- The 30-minute time limit helps prevent extended unauthorized access.
