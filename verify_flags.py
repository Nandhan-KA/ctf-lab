#!/usr/bin/env python3
"""
Flag Verification Script for CTF Lab
This script verifies that all required flag files are in place
"""

import os
import subprocess

def check_file_exists(path, description):
    """Check if a file exists and is readable"""
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
            print(f"✓ {description}: {path}")
            print(f"  Content: {content}")
            return True
        except Exception as e:
            print(f"✗ {description}: {path} - Error reading: {e}")
            return False
    else:
        print(f"✗ {description}: {path} - File not found")
        return False

def check_directory_exists(path, description):
    """Check if a directory exists and is accessible"""
    if os.path.exists(path) and os.path.isdir(path):
        try:
            files = os.listdir(path)
            print(f"✓ {description}: {path}")
            print(f"  Contents: {files}")
            return True
        except Exception as e:
            print(f"✗ {description}: {path} - Error accessing: {e}")
            return False
    else:
        print(f"✗ {description}: {path} - Directory not found")
        return False

def verify_flags():
    """Verify all required flag files are in place"""
    print("=" * 60)
    print("CTF LAB FLAG VERIFICATION")
    print("=" * 60)
    
    all_good = True
    
    # Check FTP flags
    print("\n📁 FTP FLAGS:")
    print("-" * 30)
    all_good &= check_file_exists("/home/ftpuser/flag.txt", "FTP Main Flag")
    all_good &= check_file_exists("/home/ftpuser/anonymous_flag.txt", "FTP Anonymous Flag")
    
    # Check SMB structure and flags
    print("\n📁 SMB STRUCTURE:")
    print("-" * 30)
    all_good &= check_directory_exists("/srv/smb", "SMB Root Directory")
    all_good &= check_directory_exists("/srv/smb/idk", "SMB IDK Folder")
    all_good &= check_directory_exists("/srv/smb/thisisit", "SMB ThisIsIt Folder")
    all_good &= check_directory_exists("/srv/smb/thisisnot", "SMB ThisIsNot Folder")
    
    print("\n📁 SMB FLAGS:")
    print("-" * 30)
    all_good &= check_file_exists("/srv/smb/idk/flag.txt", "SMB IDK Flag")
    all_good &= check_file_exists("/srv/smb/thisisit/flag.txt", "SMB ThisIsIt Flag")
    all_good &= check_file_exists("/srv/smb/thisisnot/flag.txt", "SMB ThisIsNot Flag (CORRECT)")
    all_good &= check_file_exists("/srv/smb/credentials_flag.txt", "SMB Credentials Root Flag")
    
    # Check Telnet flags
    print("\n📁 TELNET FLAGS:")
    print("-" * 30)
    all_good &= check_file_exists("/home/telnetuser/flag_correct.txt", "Telnet Correct Flag")
    all_good &= check_file_exists("/home/telnetuser/flag_wrong.txt", "Telnet Wrong Flag")
    
    # Check per-student flag directories
    print("\n📁 PER-STUDENT FLAG DIRECTORIES:")
    print("-" * 30)
    all_good &= check_directory_exists("/home/ftpuser/flags", "FTP Per-Student Flags")
    all_good &= check_directory_exists("/home/telnetuser/flags", "Telnet Per-Student Flags")
    all_good &= check_directory_exists("/srv/smb/flags", "SMB Per-Student Flags")
    
    # Check service configurations
    print("\n🔧 SERVICE CONFIGURATIONS:")
    print("-" * 30)
    
    # Check if services are running
    services = [
        ("vsftpd", "FTP Service"),
        ("smbd", "SMB Service"),
        ("xinetd", "Telnet Service (via xinetd)")
    ]
    
    for service, description in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ {description}: {service} is running")
            else:
                print(f"✗ {description}: {service} is not running")
                all_good = False
        except Exception as e:
            print(f"✗ {description}: {service} - Error checking: {e}")
            all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ALL FLAGS AND SERVICES VERIFIED SUCCESSFULLY!")
        print("Students should be able to find all required flags during the CTF.")
    else:
        print("⚠️  SOME ISSUES FOUND!")
        print("Please check the errors above and run setup.sh again if needed.")
    
    print("=" * 60)
    
    return all_good

if __name__ == "__main__":
    try:
        verify_flags()
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
