#!/usr/bin/env python3
"""
Demo script for CTF Lab Simulation System
Shows the key features and how to use them
"""

import os
import sys

def print_header():
    """Print demo header"""
    print("🔒 CTF Lab Simulation System - Demo")
    print("=" * 50)
    print()

def show_features():
    """Show system features"""
    print("🎯 Key Features:")
    print("  ✅ Web-based terminal emulator")
    print("  ✅ Simulated FTP, SMB, Telnet services")
    print("  ✅ Pre-configured flags and responses")
    print("  ✅ 30-minute exam timer")
    print("  ✅ Student management system")
    print("  ✅ Answer submission and scoring")
    print("  ✅ No real servers required")
    print()

def show_commands():
    """Show available commands"""
    print("🎮 Available Terminal Commands:")
    print("  📁 Basic Commands:")
    print("    • ls                    - List files and directories")
    print("    • cd [directory]        - Change directory")
    print("    • pwd                   - Show current directory")
    print("    • clear                 - Clear terminal")
    print("    • help                  - Show available commands")
    print()
    print("  🌐 Network Tools:")
    print("    • nmap 13.62.104.182    - Network scanner")
    print("    • ftp 13.62.104.182     - FTP client")
    print("    • smbclient //13.62.104.182/credentials - SMB client")
    print("    • telnet 13.62.104.182  - Telnet client")
    print()

def show_flags():
    """Show hidden flags"""
    print("🏴 Hidden Flags:")
    print("  🔍 FTP Flag:")
    print("    • Command: ftp 13.62.104.182")
    print("    • Username: Anonymous")
    print("    • Password: 12345678")
    print("    • Flag: FLAG{Anonymous_ftp_flag}")
    print()
    print("  📁 SMB Flag:")
    print("    • Command: smbclient //13.62.104.182/credentials")
    print("    • Navigate to: thisisnot folder")
    print("    • Flag: FLAG{smb_credentials_flag}")
    print()
    print("  🔌 Telnet Flag:")
    print("    • Command: telnet 13.62.104.182")
    print("    • Username: root")
    print("    • Password: (empty)")
    print("    • Flag: FLAG{telnet_root_flag}")
    print()

def show_exam_questions():
    """Show exam questions"""
    print("📝 Exam Questions:")
    print("  1. Network Services: List all open services from nmap scan")
    print("  2. FTP Flag: Retrieve flag from FTP server")
    print("  3. SMB Flag: Retrieve flag from SMB share")
    print("  4. Telnet Flag: Retrieve flag from Telnet service")
    print("  5. Service Versions: Identify service versions")
    print("  6. Operating System: Identify target OS")
    print()

def show_setup_instructions():
    """Show setup instructions"""
    print("🚀 Setup Instructions:")
    print("  1. Install dependencies:")
    print("     cd web")
    print("     pip install -r requirements.txt")
    print()
    print("  2. Add students to students.txt:")
    print("     Format: RollNumber,Name")
    print("     Example: 21CS001,John Doe")
    print()
    print("  3. Run setup script:")
    print("     ./setup.sh")
    print()
    print("  4. Start the application:")
    print("     cd web")
    print("     python app.py")
    print()
    print("  5. Access the application:")
    print("     http://localhost:5000")
    print()

def show_student_workflow():
    """Show student workflow"""
    print("👨‍🎓 Student Workflow:")
    print("  1. 📱 Login with roll number and password")
    print("  2. 💻 Access web-based terminal")
    print("  3. 🔍 Run commands to explore services")
    print("  4. 🏴 Discover hidden flags")
    print("  5. 📝 Submit answers via web form")
    print("  6. ⏰ Complete within 30-minute time limit")
    print()

def show_admin_features():
    """Show admin features"""
    print("👨‍💼 Admin Features:")
    print("  📊 View student submissions and scores")
    print("  👥 Manage student accounts")
    print("  🗄️ Database management")
    print("  ⏱️ Monitor exam progress")
    print("  📈 Generate reports")
    print()

def show_benefits():
    """Show system benefits"""
    print("✨ Benefits of Simulation:")
    print("  🛡️ No real servers required")
    print("  🔄 Consistent experience for all students")
    print("  🚀 Easy setup and deployment")
    print("  📈 Scalable for large classes")
    print("  💰 Cost-effective")
    print("  🔒 Safe learning environment")
    print()

def main():
    """Run the demo"""
    print_header()
    show_features()
    show_commands()
    show_flags()
    show_exam_questions()
    show_student_workflow()
    show_admin_features()
    show_benefits()
    show_setup_instructions()
    
    print("🎉 Demo Complete!")
    print("\n💡 To get started:")
    print("  1. Run: python test_system.py")
    print("  2. Run: ./setup.sh")
    print("  3. Start: cd web && python app.py")
    print("  4. Open: http://localhost:5000")

if __name__ == "__main__":
    main()
