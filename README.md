# CTF Exam Lab (Beginner)

A self-contained beginner-friendly CTF lab focused on enumerating FTP, Telnet, and SMB, capturing a per-student flag, and submitting it via a simple web portal.

## Features
- Automated setup on Ubuntu (WSL or VPS) via `setup.sh`.
- Services: FTP (`vsftpd`), Telnet (`telnetd`), SMB (Samba).
- Web portal (Flask + Gunicorn + Nginx) for registration/login and flag submission.
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
│   │   ├── success.html
│   │   └── fail.html
│   └── requirements.txt
├── students.txt              # CSV: Name,Email
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
   - Default credentials for services (share with students):
     - FTP: user `ftpuser`, pass `ftpuserpass`
     - Telnet: user `telnetuser`, pass `telnetuserpass`
     - SMB: user `smbuser`, pass `smbuserpass`, share `\\<IP>\ctfshare`

### Note on WSL
If running under WSL, you may need to enable systemd for services (xinetd/inetd, smbd, nginx) to start automatically. See Microsoft docs on enabling systemd in WSL, or run the web app manually:
```bash
cd web
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
# then browse http://localhost:5000
```

## Instructor Notes
- Flags are generated per student in the format `FLAG{Name_randomHex}`.
- Flags are placed here (by student ID in DB):
  - FTP: `/home/ftpuser/flags/flag_<id>.txt`
  - Telnet: `/home/telnetuser/flags/flag_<id>.txt`
  - SMB: `/srv/smb/flags/flag_<id>.txt`
- The web app validates submitted flags against the SQLite DB at `web/ctf_lab.db`.

### Add/Update Students
- Edit `students.txt` and re-run `sudo bash setup.sh`. Existing emails will be updated with new flags.

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
2. Register or login with your email from the roster.
3. You will see your Student ID. Your flag files are named `flag_<id>.txt`.
4. Scan the target IP (below) and enumerate services.
5. Retrieve your flag and submit it via the portal.

### Example Nmap Commands
- Fast top ports:
  ```bash
  nmap -sS -Pn -T4 <server_public_ip>
  ```
- Full TCP port scan (slower):
  ```bash
  nmap -sS -p- -T4 <server_public_ip>
  ```
- Service/version detection:
  ```bash
  nmap -sV -sC -p 21,23,445 <server_public_ip>
  ```

### Example Service Access
- FTP (download your flag):
  ```bash
  ftp <server_public_ip>
  Name: ftpuser
  Password: ftpuserpass
  get /home/ftpuser/flags/flag_<id>.txt
  ```
- Telnet (read your flag):
  ```bash
  telnet <server_public_ip>
  login: telnetuser
  password: telnetuserpass
  cat /home/telnetuser/flags/flag_<id>.txt
  ```
- SMB (mount or list share):
  ```bash
  smbclient \\\\<server_public_ip>\\ctfshare -U smbuser
  # password: smbuserpass
  cd flags
  get flag_<id>.txt
  ```

## Local Web App Testing (Optional)
If you only want to test the Flask app locally (without services), use Docker Compose:
```bash
docker compose up --build
# Open http://localhost:5000
```
Note: The compose setup does not run FTP/Telnet/SMB; it only starts the web app.

## Security Notes
- This lab intentionally exposes legacy services (FTP, Telnet). Run it on an isolated VPS or lab network.
- Use firewall rules to restrict access if needed.
- Do not reuse credentials elsewhere.
