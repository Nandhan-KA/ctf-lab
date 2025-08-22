# CTF Lab Flag Placement Guide

This document shows exactly where each flag is placed for students to find during the CTF exam.

## Flag Locations by Question

### Question 1: Service Enumeration
**Question:** What are all the services running on the IP 13.62.104.182?
**Answer:** ftp, ssh, http, telnet
**Method:** Students must use nmap or similar tools to scan the target IP

### Question 2: FTP Flag
**Question:** Flag for FTP (connect using user: Anonymous, pass: 12345678)
**Answer:** FLAG{Anonymous_ftp_flag}
**Location:** 
- `/home/ftpuser/flag.txt`
- `/home/ftpuser/anonymous_flag.txt`

**Student Access Method:**
```bash
ftp 13.62.104.182
# Username: Anonymous
# Password: 12345678
get flag.txt
get anonymous_flag.txt
```

### Question 3: SMB Flag
**Question:** Flag for SMB (use smbclient //13.62.104.182/credentials, check all three folders: idk, thisisit, thisisnot - the flag in thisisnot folder is the answer)
**Answer:** FLAG{smb_credentials_flag}
**Location:** 
- `/srv/smb/thisisnot/flag.txt` ← **CORRECT ANSWER**
- `/srv/smb/idk/flag.txt` (contains FLAG{wrong_flag_1})
- `/srv/smb/thisisit/flag.txt` (contains FLAG{wrong_flag_2})

**Student Access Method:**
```bash
smbclient //13.62.104.182/credentials -U smbuser
# Password: smbuserpass

# Navigate through folders
ls
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

### Question 4: Telnet Flag
**Question:** Telnet flag (connect using root without password, there are 2 flags - find the correct one)
**Answer:** FLAG{telnet_root_flag}
**Location:**
- `/home/telnetuser/flag_correct.txt` ← **CORRECT ANSWER**
- `/home/telnetuser/flag_wrong.txt` (contains FLAG{wrong_telnet_flag})

**Student Access Method:**
```bash
telnet 13.62.104.182
# Login: root
# Password: (none required)

cat flag_correct.txt  # This is the correct answer
cat flag_wrong.txt    # This is the wrong flag
```

### Question 5: Service Versions
**Question:** What is the version of FTP, SMB, and Telnet running on the server 13.62.104.182?
**Answer:** vsftpd 2.0.8 or later, SMB version info, telnet closed
**Method:** Students must use version detection tools like nmap

**Expected nmap output:**
```
21/tcp open   ftp     vsftpd 2.0.8 or later
22/tcp open   ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
23/tcp closed telnet
80/tcp open   http    nginx 1.18.0 (Ubuntu)
Service Info: Host: Welcome; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Question 6: Operating System
**Question:** What type of operating system is running on the server?
**Answer:** Linux
**Method:** Students can determine this from service banners and nmap output

## Complete File Structure

```
/home/ftpuser/
├── flag.txt                    # FLAG{Anonymous_ftp_flag}
├── anonymous_flag.txt          # FLAG{Anonymous_ftp_flag}
└── flags/                      # Per-student flags
    ├── flag_1.txt
    ├── flag_2.txt
    └── ...

/home/telnetuser/
├── flag_correct.txt            # FLAG{telnet_root_flag} ← CORRECT
├── flag_wrong.txt              # FLAG{wrong_telnet_flag} ← WRONG
└── flags/                      # Per-student flags
    ├── flag_1.txt
    ├── flag_2.txt
    └── ...

/srv/smb/
├── credentials_flag.txt        # FLAG{smb_credentials_flag}
├── idk_flag.txt               # FLAG{wrong_flag_1}
├── thisisit_flag.txt          # FLAG{wrong_flag_2}
├── thisisnot_flag.txt         # FLAG{smb_credentials_flag}
├── idk/
│   └── flag.txt               # FLAG{wrong_flag_1}
├── thisisit/
│   └── flag.txt               # FLAG{wrong_flag_2}
├── thisisnot/
│   └── flag.txt               # FLAG{smb_credentials_flag} ← CORRECT
└── flags/                      # Per-student flags
    ├── flag_1.txt
    ├── flag_2.txt
    └── ...
```

## SMB Share Access

Students can access the SMB shares using:

```bash
# Main credentials share (contains the folders)
smbclient //13.62.104.182/credentials -U smbuser

# Alternative shares (same content, different names)
smbclient //13.62.104.182/admin -U smbuser
smbclient //13.62.104.182/IC -U smbuser
```

## Important Notes

1. **FTP Anonymous Access:** Students must use "Anonymous" as username and "12345678" as password
2. **SMB Navigation:** Students must explore all three folders to find the correct flag in "thisisnot"
3. **Telnet Root Access:** Students connect as root without password and must identify the correct flag
4. **Version Detection:** Students need to use proper enumeration tools to get service versions
5. **OS Detection:** Students can determine the OS from service banners and responses

## Student Workflow

1. **Scan the target** (13.62.104.182) to identify running services
2. **Access FTP** anonymously to retrieve the flag
3. **Access SMB** credentials share and navigate through folders
4. **Access Telnet** as root to find the correct flag
5. **Use version detection** tools to identify service versions
6. **Determine OS** from service responses
7. **Submit all answers** within the 30-minute time limit

## Verification Commands

Instructors can verify flag placement using:

```bash
# Check FTP flags
ls -la /home/ftpuser/flag*.txt
cat /home/ftpuser/flag.txt

# Check SMB flags
ls -la /srv/smb/*/flag*.txt
cat /srv/smb/thisisnot/flag.txt

# Check Telnet flags
ls -la /home/telnetuser/flag*.txt
cat /home/telnetuser/flag_correct.txt
```
