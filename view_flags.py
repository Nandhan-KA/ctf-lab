#!/usr/bin/env python3
"""
Utility script to view dynamic flags for each student
"""

import hashlib
import os

def generate_flags(roll_number):
    """Generate unique flags for a student based on their roll number"""
    hash_base = hashlib.md5(roll_number.encode()).hexdigest()[:8]
    
    return {
        'ftp_flag': f'FLAG{{ftp_{hash_base}_flag}}',
        'smb_flag': f'FLAG{{smb_{hash_base}_flag}}',
        'telnet_flag': f'FLAG{{telnet_{hash_base}_flag}}'
    }

def main():
    print("🔒 CTF Lab - Dynamic Flag Generator")
    print("=" * 50)
    print()
    
    # Read students from file
    students_file = 'students.txt'
    if not os.path.exists(students_file):
        print(f"❌ {students_file} not found!")
        return
    
    print("📋 Student Flags:")
    print("-" * 50)
    
    with open(students_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    roll_number = parts[0].strip()
                    name = parts[1].strip()
                    
                    flags = generate_flags(roll_number)
                    
                    print(f"👤 {name} ({roll_number})")
                    print(f"   FTP:    {flags['ftp_flag']}")
                    print(f"   SMB:    {flags['smb_flag']}")
                    print(f"   Telnet: {flags['telnet_flag']}")
                    print()
    
    print("💡 Note: These flags are automatically generated based on roll number")
    print("   Each student gets unique flags that cannot be shared with others")

if __name__ == "__main__":
    main()
