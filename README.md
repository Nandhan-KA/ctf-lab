# CTF Lab - Simulation-Based System

A web-based Capture The Flag (CTF) lab simulation that provides students with a realistic terminal environment to practice penetration testing techniques without requiring real servers.

## Features

- **Web-based Terminal Emulator**: Full-featured terminal interface with command history and tab completion
- **Simulated Services**: FTP, SMB, Telnet, and HTTP services with realistic responses
- **Pre-configured Flags**: Hidden flags in various services for students to discover
- **Timer System**: 30-minute time limit for exam completion
- **Student Management**: Individual login system with progress tracking
- **Answer Submission**: Web form for submitting discovered flags and answers

## How It Works

### For Students
1. **Login**: Students log in with their roll number and password
2. **Terminal Access**: They're redirected to a web-based terminal emulator
3. **Command Execution**: Students can run commands like:
   - `nmap 13.62.104.182` - Network scanning
   - `ftp 13.62.104.182` - FTP client simulation
   - `smbclient //13.62.104.182/credentials` - SMB client simulation
   - `telnet 13.62.104.182` - Telnet client simulation
4. **Flag Discovery**: Students explore services to find hidden flags
5. **Answer Submission**: Submit discovered flags and answers via web form

### For Administrators
- **Student Management**: Add students via `students.txt` file
- **Progress Tracking**: Monitor student progress and submissions
- **Database**: All data stored in SQLite database
- **Results**: View student scores and answers

## Available Commands

### Basic Commands
- `ls` - List files and directories
- `cd [directory]` - Change directory
- `pwd` - Show current directory
- `clear` - Clear terminal
- `help` - Show available commands

### Network Tools
- `nmap [target]` - Network scanner (target: 13.62.104.182)
- `ftp [target]` - FTP client (target: 13.62.104.182)
- `smbclient [share]` - SMB client (share: //13.62.104.182/credentials)
- `telnet [target]` - Telnet client (target: 13.62.104.182)

## Target Information

- **IP Address**: 13.62.104.182
- **Services**: FTP, SSH, Telnet, HTTP
- **FTP Credentials**: Anonymous/12345678
- **SMB Share**: //13.62.104.182/credentials
- **Telnet Credentials**: root/(empty password)

## Hidden Flags

1. **FTP Flag**: `FLAG{Anonymous_ftp_flag}` - Found in FTP root directory
2. **SMB Flag**: `FLAG{smb_credentials_flag}` - Found in //13.62.104.182/credentials/thisisnot/
3. **Telnet Flag**: `FLAG{telnet_root_flag}` - Found in telnet root directory

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   cd web
   pip install -r requirements.txt
   ```

2. **Add Students**:
   Edit `students.txt` file with student roll numbers and names

3. **Run Setup Script**:
   ```bash
   ./setup.sh
   ```

4. **Start the Application**:
   ```bash
   cd web
   python app.py
   ```

5. **Access the Application**:
   - Open browser to `http://localhost:5000`
   - Students can change passwords at `/change_password`
   - Admin can view results at `/view_database.py`

## File Structure

```
ctf-lab/
├── web/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── templates/
│   │   ├── terminal.html      # Terminal emulator interface
│   │   ├── submit.html        # Answer submission form
│   │   ├── results.html       # Results display
│   │   └── ...               # Other templates
│   └── ctf_lab.db            # SQLite database
├── students.txt              # Student list
├── setup.sh                  # Setup script
├── verify_flags.py           # Flag verification utility
└── view_database.py          # Database viewer
```

## Exam Questions

Students must answer 6 questions:

1. **Network Services**: List all open services from nmap scan
2. **FTP Flag**: Retrieve flag from FTP server
3. **SMB Flag**: Retrieve flag from SMB share
4. **Telnet Flag**: Retrieve flag from Telnet service
5. **Service Versions**: Identify service versions
6. **Operating System**: Identify target OS

## Security Features

- **Session Management**: Secure session handling with time limits
- **Password Hashing**: Student passwords are hashed using Werkzeug
- **Input Validation**: All inputs are validated and sanitized
- **Time Limits**: 30-minute exam timer with automatic submission

## Benefits of Simulation

- **No Real Servers**: No need to maintain vulnerable servers
- **Consistent Environment**: All students get the same experience
- **Safe Learning**: No risk of network issues or server downtime
- **Scalable**: Can handle multiple students simultaneously
- **Easy Setup**: Simple deployment without complex infrastructure

## Customization

- **Add New Commands**: Extend the terminal emulator with new commands
- **Modify Flags**: Change flag locations and content
- **Add Services**: Implement additional simulated services
- **Custom Questions**: Modify exam questions and scoring
- **UI Customization**: Modify terminal appearance and behavior

## Troubleshooting

- **Database Issues**: Delete `ctf_lab.db` and restart to reset
- **Student Login**: Check `students.txt` format and password hashing
- **Terminal Issues**: Clear browser cache and refresh page
- **Timer Issues**: Check system time and session management

## License

This project is designed for educational purposes. Use responsibly and only in controlled environments.
