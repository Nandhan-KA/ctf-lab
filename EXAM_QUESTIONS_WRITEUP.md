# CTF Lab Exam Questions - Complete Writeup

This document provides comprehensive solutions and methodologies for all 6 questions in the CTF Lab exam.

## **Question 1: Service Enumeration**
**Question:** What are all the services running on the IP 13.62.104.182?

**Expected Answer:** `ftp, ssh, http, telnet`

**Methodology:**
1. **Port Scanning:** Use nmap to discover open ports
2. **Service Identification:** Identify what services are running on each port
3. **Documentation:** List all discovered services

**Commands to Use:**
```bash
# Basic port scan
nmap -sS -Pn -T4 13.62.104.182

# Service version detection
nmap -sV -sC -p- 13.62.104.182

# Quick top ports scan
nmap -sS -Pn -T4 --top-ports 1000 13.62.104.182
```

**Expected Output:**
```
Starting Nmap 7.80 ( https://nmap.org )
Nmap scan report for 13.62.104.182
Host is up (0.000s latency).
Not shown: 996 closed ports
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
23/tcp  open  telnet
80/tcp  open  http
```

**What Students Should Do:**
- Run nmap scan on target IP
- Identify all open ports
- List services: ftp, ssh, http, telnet
- Note that telnet might show as closed in some scans

---

## **Question 2: FTP Flag Retrieval**
**Question:** Flag for FTP (connect using user: Anonymous, pass: 12345678)

**Expected Answer:** `FLAG{Anonymous_ftp_flag}`

**Methodology:**
1. **Connect to FTP:** Use ftp client to connect anonymously
2. **Authentication:** Use "Anonymous" as username and "12345678" as password
3. **File Listing:** List available files
4. **Download Flag:** Retrieve the flag file

**Commands to Use:**
```bash
# Connect to FTP
ftp 13.62.104.182

# Username: Anonymous
# Password: 12345678

# List files
ls
dir

# Download flag file
get flag.txt
get anonymous_flag.txt

# Exit FTP
quit
```

**Expected Output:**
```
Connected to 13.62.104.182.
220 Welcome to the CTF Lab FTP server.
Name (13.62.104.182:user): Anonymous
331 Please specify the password.
Password: 12345678
230 Login successful.
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 ftpuser   ftpuser         25 Jan 01 12:00 flag.txt
-rw-r--r--    1 ftpuser   ftpuser         25 Jan 01 12:00 anonymous_flag.txt
226 Directory send OK.
ftp> get flag.txt
local: flag.txt remote: flag.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for flag.txt (25 bytes).
226 Transfer complete.
25 bytes received in 0.00 secs (25.00 Kbytes/sec)
```

**What Students Should Do:**
- Connect to FTP anonymously
- Use correct credentials
- Download flag files
- Read flag content

---

## **Question 3: SMB Flag Retrieval**
**Question:** Flag for SMB (use smbclient //13.62.104.182/credentials, check all three folders: idk, thisisit, thisisnot - the flag in thisisnot folder is the answer)

**Expected Answer:** `FLAG{smb_credentials_flag}`

**Methodology:**
1. **Connect to SMB:** Use smbclient to access the credentials share
2. **Authentication:** Use smbuser credentials
3. **Folder Navigation:** Explore all three folders systematically
4. **Flag Identification:** Find the correct flag in the "thisisnot" folder

**Commands to Use:**
```bash
# Connect to SMB credentials share
smbclient //13.62.104.182/credentials -U smbuser

# Password: smbuserpass

# List contents
ls

# Navigate through folders
cd idk
ls
get flag.txt
cd ../thisisit
ls
get flag.txt
cd ../thisisnot
ls
get flag.txt  # This is the correct answer
```

**Expected Output:**
```
Domain=[WORKGROUP] OS=[Windows 6.1] Server=[Samba 4.15.13]
smb: \> ls
  .                                   D        0  Jan 01 12:00:00
  ..                                  D        0  Jan 01 12:00:00
  idk                                 D        0  Jan 01 12:00:00
  thisisit                            D        0  Jan 01 12:00:00
  thisisnot                           D        0  Jan 01 12:00:00
  credentials_flag.txt                N       25  Jan 01 12:00:00

smb: \> cd idk
smb: \idk\> ls
  .                                   D        0  Jan 01 12:00:00
  ..                                  D        0  Jan 01 12:00:00
  flag.txt                            N       25  Jan 01 12:00:00

smb: \idk\> get flag.txt
getting file \idk\flag.txt of size 25 as flag.txt (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)

smb: \idk\> cd ../thisisit
smb: \thisisit\> ls
  .                                   D        0  Jan 01 12:00:00
  ..                                   D        0  Jan 01 12:00:00
  flag.txt                            N       25  Jan 01 12:00:00

smb: \thisisit\> get flag.txt
getting file \thisisit\flag.txt of size 25 as flag.txt (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)

smb: \thisisnot\> cd ../thisisnot
smb: \thisisnot\> ls
  .                                   D        0  Jan 01 12:00:00
  ..                                   D        0  Jan 01 12:00:00
  flag.txt                            N       25  Jan 01 12:00:00

smb: \thisisnot\> get flag.txt
getting file \thisisnot\flag.txt of size 25 as flag.txt (0.0 KiloBytes/sec) (average 0.0 KiloBytes/sec)
```

**What Students Should Do:**
- Connect to SMB credentials share
- Navigate through all three folders
- Download flags from each folder
- Identify the correct flag (from thisisnot folder)

---

## **Question 4: Telnet Flag Retrieval**
**Question:** Telnet flag (connect using root without password, there are 2 flags - find the correct one)

**Expected Answer:** `FLAG{telnet_root_flag}`

**Methodology:**
1. **Connect to Telnet:** Use telnet client to connect to target
2. **Root Login:** Login as root without password
3. **File Exploration:** Find and examine both flag files
4. **Flag Identification:** Determine which flag is correct

**Commands to Use:**
```bash
# Connect to telnet
telnet 13.62.104.182

# Login: root
# Password: (none required)

# List files
ls -la
cat flag_correct.txt  # This is the correct answer
cat flag_wrong.txt    # This is the wrong flag
```

**Expected Output:**
```
Trying 13.62.104.182...
Connected to 13.62.104.182.
Escape character is '^]'.

Welcome to CTF Lab Telnet Server
login: root
Password: 
Welcome root!

root@ctf-lab:~$ ls -la
total 16
drwxr-xr-x 2 telnetuser telnetuser 4096 Jan 01 12:00 .
drwxr-xr-x 3 root       root       4096 Jan 01 12:00 ..
-rw-r--r-- 1 telnetuser telnetuser   25 Jan 01 12:00 flag_correct.txt
-rw-r--r-- 1 telnetuser telnetuser   25 Jan 01 12:00 flag_wrong.txt

root@ctf-lab:~$ cat flag_correct.txt
FLAG{telnet_root_flag}

root@ctf-lab:~$ cat flag_wrong.txt
FLAG{wrong_telnet_flag}
```

**What Students Should Do:**
- Connect via telnet
- Login as root (no password)
- Examine both flag files
- Identify the correct flag

---

## **Question 5: Service Version Detection**
**Question:** What is the version of FTP, SMB, and Telnet running on the server 13.62.104.182?

**Expected Answer:** `vsftpd 2.0.8 or later, SMB version info, telnet closed`

**Methodology:**
1. **Version Scanning:** Use nmap with version detection
2. **Service Analysis:** Examine service banners and responses
3. **Information Gathering:** Collect version information from each service
4. **Documentation:** Record all version details

**Commands to Use:**
```bash
# Comprehensive version detection
nmap -sV -sC -p 21,23,445 13.62.104.182

# Detailed service enumeration
nmap -sV -sC -p- --version-intensity 9 13.62.104.182

# Specific port version detection
nmap -sV -p 21,23,445 13.62.104.182
```

**Expected Output:**
```
Starting Nmap 7.80 ( https://nmap.org )
Nmap scan report for 13.62.104.182
Host is up (0.000s latency).
Not shown: 65531 closed ports
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp        vsftpd 2.0.8 or later
22/tcp  open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
23/tcp  closed telnet
80/tcp  open  http       nginx 1.18.0 (Ubuntu)
445/tcp open  netbios-ssn Samba smbd 4.15.13 (workgroup: WORKGROUP)
Service Info: Host: Welcome; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

**What Students Should Do:**
- Use nmap version detection
- Focus on ports 21, 23, 445
- Record FTP version (vsftpd 2.0.8 or later)
- Note telnet status (closed)
- Record SMB version information

---

## **Question 6: Operating System Detection**
**Question:** What type of operating system is running on the server?

**Expected Answer:** `Linux`

**Methodology:**
1. **OS Fingerprinting:** Use nmap OS detection
2. **Service Banner Analysis:** Examine service responses for OS hints
3. **Multiple Sources:** Gather OS information from various services
4. **Verification:** Confirm OS type through multiple indicators

**Commands to Use:**
```bash
# OS detection
nmap -O 13.62.104.182

# Service banner analysis
nmap -sV -sC 13.62.104.182

# SSH banner analysis
nc 13.62.104.182 22

# HTTP server analysis
curl -I http://13.62.104.182/
```

**Expected Output:**
```
Starting Nmap 7.80 ( https://nmap.org )
Nmap scan report for 13.62.104.182
Host is up (0.000s latency).
Not shown: 65531 closed ports
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp        vsftpd 2.0.8 or later
22/tcp  open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
23/tcp  closed telnet
80/tcp  open  http       nginx 1.18.0 (Ubuntu)
445/tcp open  netbios-ssn Samba smbd 4.15.13 (workgroup: WORKGROUP)
Service Info: Host: Welcome; OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS CPE: cpe:/o:linux:linux_kernel
OS details: Linux 5.4.0 - 5.15.0
```

**What Students Should Do:**
- Use nmap OS detection
- Analyze service banners
- Look for Linux indicators
- Confirm through multiple sources

---

## **Complete Student Workflow**

### **Step 1: Initial Reconnaissance**
```bash
# Scan target for open ports and services
nmap -sS -sV -sC -p- 13.62.104.182
```

### **Step 2: Service Enumeration**
- Identify all running services (Question 1)
- Note service versions (Question 5)
- Determine OS type (Question 6)

### **Step 3: Flag Collection**
- Access FTP anonymously (Question 2)
- Navigate SMB shares (Question 3)
- Connect via telnet (Question 4)

### **Step 4: Answer Submission**
- Submit all 6 answers within 30 minutes
- Verify answers before submission
- Check final score

## **Tools Required**

- **nmap:** Port scanning and service detection
- **ftp client:** FTP access
- **smbclient:** SMB share access
- **telnet client:** Telnet access
- **Web browser:** Access to exam portal

## **Time Management**

- **Total Time:** 30 minutes
- **Reconnaissance:** 5-8 minutes
- **Flag Collection:** 15-20 minutes
- **Answer Submission:** 2-3 minutes
- **Verification:** 2-3 minutes

## **Scoring System**

- **Question 1:** 1 point (Service enumeration)
- **Question 2:** 1 point (FTP flag)
- **Question 3:** 1 point (SMB flag)
- **Question 4:** 1 point (Telnet flag)
- **Question 5:** 1 point (Service versions)
- **Question 6:** 1 point (OS detection)

**Total Possible Score:** 6/6 points

## **Common Mistakes to Avoid**

1. **Not scanning all ports** - Missing services
2. **Wrong credentials** - Using incorrect FTP/SMB credentials
3. **Incomplete folder exploration** - Missing the correct SMB flag
4. **Version detection issues** - Not using proper nmap flags
5. **OS misidentification** - Not verifying through multiple sources
6. **Time management** - Spending too long on one question

## **Success Tips**

1. **Start with reconnaissance** - Get the big picture first
2. **Use proper tools** - nmap with correct flags
3. **Document everything** - Keep notes of findings
4. **Verify flags** - Download and read all flag files
5. **Manage time** - Don't get stuck on one question
6. **Double-check answers** - Verify before submission
