#!/usr/bin/env bash
set -euo pipefail

# CTF Lab Setup Script
# - Installs vsftpd, telnetd, samba, python3, pip/venv, nginx
# - Creates service users (ftpuser, telnetuser, smbuser)
# - Reads students from students.txt and generates unique flags
# - Places per-student flags into each service location
# - Populates SQLite DB used by the Flask web app
# - Starts Flask app behind Nginx on port 80

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "[!] Please run as root: sudo bash setup.sh" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
WEB_DIR="$SCRIPT_DIR/web"
DB_PATH="$WEB_DIR/ctf_lab.db"
STUDENTS_FILE="$SCRIPT_DIR/students.txt"

# Default service credentials (documented to students)
FTP_USER="ftpuser"
FTP_PASS="ftpuserpass"
TELNET_USER="telnetuser"
TELNET_PASS="telnetuserpass"
SMB_USER="smbuser"
SMB_PASS="smbuserpass"

# Service directories for flags
FTP_FLAGS_DIR="/home/$FTP_USER/flags"
TELNET_FLAGS_DIR="/home/$TELNET_USER/flags"
SMB_FLAGS_DIR="/srv/smb/flags"

echo "[+] Updating apt and installing dependencies..."
apt-get update -y
apt-get install -y --no-install-recommends \
  vsftpd samba samba-common-bin nginx \
  python3 python3-venv python3-pip \
  xinetd inetutils-telnetd || true

# Fallbacks for inetd variants (in case the above failed)
apt-get install -y --no-install-recommends openbsd-inetd telnetd || true

# Ensure users exist
ensure_user() {
  local USERNAME="$1"; local HOME_DIR="$2"; local SHELL_PATH="$3"; local PASS="$4"
  if id "$USERNAME" >/dev/null 2>&1; then
    usermod -d "$HOME_DIR" -s "$SHELL_PATH" "$USERNAME" || true
  else
    useradd -m -d "$HOME_DIR" -s "$SHELL_PATH" "$USERNAME"
  fi
  echo "$USERNAME:$PASS" | chpasswd
}

echo "[+] Creating service users..."
# ftpuser needs a valid shell for vsftpd + PAM setups
ensure_user "$FTP_USER" "/home/$FTP_USER" "/bin/bash" "$FTP_PASS"
# telnetuser needs a valid shell to login over telnet
ensure_user "$TELNET_USER" "/home/$TELNET_USER" "/bin/bash" "$TELNET_PASS"
# smbuser can be no-login shell, but keep /bin/bash for simplicity
ensure_user "$SMB_USER" "/home/$SMB_USER" "/bin/bash" "$SMB_PASS"

# Directories for flags
mkdir -p "$FTP_FLAGS_DIR" "$TELNET_FLAGS_DIR" "$SMB_FLAGS_DIR"
chown -R "$FTP_USER:$FTP_USER" "/home/$FTP_USER"
chown -R "$TELNET_USER:$TELNET_USER" "/home/$TELNET_USER"
chown -R "$SMB_USER:$SMB_USER" "/srv/smb"
chmod -R 755 "/home/$FTP_USER" "/home/$TELNET_USER" "/srv/smb"

# Configure vsftpd
if [[ -f /etc/vsftpd.conf ]]; then
  cp /etc/vsftpd.conf /etc/vsftpd.conf.bak_$(date +%s) || true
fi
cat > /etc/vsftpd.conf <<'VSFTPD'
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=NO
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
allow_writeable_chroot=YES
pam_service_name=vsftpd
rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
ssl_enable=NO
userlist_enable=YES
userlist_deny=NO
userlist_file=/etc/vsftpd.userlist
ftpd_banner=Welcome to the CTF Lab FTP server.
VSFTPD

echo "$FTP_USER" > /etc/vsftpd.userlist
systemctl enable vsftpd
systemctl restart vsftpd

# Configure Telnet via xinetd or inetd
if command -v xinetd >/dev/null 2>&1; then
  echo "[+] Configuring telnet via xinetd..."
  cat > /etc/xinetd.d/telnet <<'XINETD'
service telnet
{
        flags           = REUSE
        socket_type     = stream
        wait            = no
        user            = root
        server          = /usr/sbin/in.telnetd
        log_on_failure  += USERID
        disable         = no
}
XINETD
  systemctl enable xinetd
  systemctl restart xinetd
elif systemctl list-unit-files | grep -q openbsd-inetd.service; then
  echo "[+] Configuring telnet via openbsd-inetd..."
  if ! grep -q '^telnet' /etc/inetd.conf 2>/dev/null; then
    echo "telnet stream tcp nowait root /usr/sbin/in.telnetd in.telnetd" >> /etc/inetd.conf
  fi
  systemctl enable openbsd-inetd || true
  systemctl restart openbsd-inetd || true
else
  echo "[!] Telnet daemon not found; please install xinetd or openbsd-inetd + telnetd manually." >&2
fi

# Configure Samba
if [[ -f /etc/samba/smb.conf ]]; then
  cp /etc/samba/smb.conf /etc/samba/smb.conf.bak_$(date +%s) || true
fi
cat > /etc/samba/smb.conf <<'SMB'
[global]
   server role = standalone server
   map to guest = Bad User
   log file = /var/log/samba/log.%m
   max log size = 1000
   server min protocol = SMB2
   pam password change = yes
   security = user

[ctfshare]
   path = /srv/smb
   browseable = yes
   read only = yes
   guest ok = no
   valid users = smbuser
SMB

echo -e "$SMB_PASS\n$SMB_PASS" | smbpasswd -a -s "$SMB_USER" || true
systemctl enable smbd || true
systemctl restart smbd || true

# Python environment and web app deps
mkdir -p "$WEB_DIR"
python3 -m venv "$WEB_DIR/venv"
"$WEB_DIR/venv/bin/pip" install --upgrade pip
"$WEB_DIR/venv/bin/pip" install -r "$WEB_DIR/requirements.txt"

# Ensure students file exists
if [[ ! -f "$STUDENTS_FILE" ]]; then
  cat > "$STUDENTS_FILE" <<'STUDENTS'
# One student per line, CSV format: Name,Email
Alice Example,alice@example.com
Bob Example,bob@example.com
STUDENTS
fi

# Generate flags, populate DB, and write flag files
/usr/bin/env python3 - <<PY
import csv, os, sqlite3, secrets, time
DB_PATH = os.environ.get('DB_PATH', r"$DB_PATH")
STUDENTS_FILE = os.environ.get('STUDENTS_FILE', r"$STUDENTS_FILE")
FTP_FLAGS_DIR = os.environ.get('FTP_FLAGS_DIR', r"$FTP_FLAGS_DIR")
TELNET_FLAGS_DIR = os.environ.get('TELNET_FLAGS_DIR', r"$TELNET_FLAGS_DIR")
SMB_FLAGS_DIR = os.environ.get('SMB_FLAGS_DIR', r"$SMB_FLAGS_DIR")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(
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

created = 0
updated = 0
with open(STUDENTS_FILE, newline='') as f:
    for raw in f:
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        name, email = parts[0], parts[1].lower()
        flag = f"FLAG{{{name.replace(' ', '')}_{secrets.token_hex(8)}}}"
        ts = time.strftime('%Y-%m-%d %H:%M:%S')

        # Upsert logic
        cur = conn.execute("SELECT id FROM students WHERE email = ?", (email,))
        row = cur.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO students (name, email, flag, timestamp) VALUES (?, ?, ?, ?)",
                (name, email, flag, ts)
            )
            student_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            created += 1
        else:
            student_id = row[0]
            conn.execute(
                "UPDATE students SET name=?, flag=?, timestamp=? WHERE id=?",
                (name, flag, ts, student_id)
            )
            updated += 1
        conn.commit()

        # Write flags to service locations (per-student files)
        for base, label in (
            (FTP_FLAGS_DIR, 'FTP'),
            (TELNET_FLAGS_DIR, 'TELNET'),
            (SMB_FLAGS_DIR, 'SMB'),
        ):
            os.makedirs(base, exist_ok=True)
            path = os.path.join(base, f"flag_{student_id}.txt")
            with open(path, 'w', encoding='utf-8') as outf:
                outf.write(flag + "\n")

print(f"DB path: {DB_PATH}")
print(f"Students created: {created}, updated: {updated}")
PY

# Ensure flag files are owned by service users
chown -R "$FTP_USER:$FTP_USER" "$FTP_FLAGS_DIR"
chown -R "$TELNET_USER:$TELNET_USER" "$TELNET_FLAGS_DIR"
chown -R "$SMB_USER:$SMB_USER" "$SMB_FLAGS_DIR"

# Permissions for web app
chown -R www-data:www-data "$WEB_DIR"
# Keep source files readable; DB must be writable by www-data
chmod 755 "$WEB_DIR"
chmod 644 "$WEB_DIR"/*.py 2>/dev/null || true
chmod 664 "$DB_PATH" 2>/dev/null || true

# Systemd service for gunicorn
SERVICE_FILE="/etc/systemd/system/ctf-lab.service"
cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=CTF Lab Flask App (gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$WEB_DIR
Environment=PATH=$WEB_DIR/venv/bin
ExecStart=$WEB_DIR/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable ctf-lab
systemctl restart ctf-lab

# Nginx reverse proxy on port 80
NGINX_SITE="/etc/nginx/sites-available/ctf-lab"
cat > "$NGINX_SITE" <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

ln -sf "$NGINX_SITE" /etc/nginx/sites-enabled/ctf-lab
if [[ -f /etc/nginx/sites-enabled/default ]]; then rm -f /etc/nginx/sites-enabled/default; fi
nginx -t
systemctl enable nginx
systemctl reload nginx || systemctl restart nginx

IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}')

cat <<INFO

[✓] CTF Lab setup complete.

Web portal:  http://$IP_ADDR/  (or use the public IP provided by your VPS)

Service logins for students:
- FTP    -> user: $FTP_USER    pass: $FTP_PASS
- Telnet -> user: $TELNET_USER pass: $TELNET_PASS
- SMB    -> user: $SMB_USER    pass: $SMB_PASS   share: \\${IP_ADDR}\ctfshare

Flag file paths per student (ID is their DB id):
- FTP:    /home/$FTP_USER/flags/flag_<id>.txt
- Telnet: /home/$TELNET_USER/flags/flag_<id>.txt
- SMB:    /srv/smb/flags/flag_<id>.txt  (via share ctfshare/flags/flag_<id>.txt)

Re-run this script to regenerate flags from students.txt.
INFO
