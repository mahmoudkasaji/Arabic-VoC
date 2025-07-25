#!/usr/bin/env python3
"""
Direct Gmail Connection Test Script
Tests Gmail SMTP connection with detailed debugging
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_gmail_connection():
    """Test Gmail SMTP connection with detailed logging"""
    
    # Get credentials
    username = os.getenv("GMAIL_USERNAME")
    password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"Testing Gmail connection...")
    print(f"Username: {username}")
    print(f"Password length: {len(password) if password else 0}")
    print(f"Password format: {'*' * len(password) if password else 'None'}")
    
    if not username or not password:
        print("❌ Missing credentials")
        return False
    
    try:
        print("\n1. Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        
        print("2. Starting TLS...")
        server.starttls()
        
        print("3. Attempting login...")
        server.login(username, password)
        
        print("✅ Gmail connection successful!")
        
        print("4. Testing email send...")
        msg = MIMEText("Test email from Voice of Customer Platform")
        msg['Subject'] = "Gmail Connection Test"
        msg['From'] = username
        msg['To'] = username  # Send to self
        
        server.send_message(msg)
        print("✅ Test email sent successfully!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure 2-Factor Authentication is enabled on your Google Account")
        print("2. Generate a new App Password:")
        print("   - Go to Google Account → Security → App passwords")
        print("   - Select 'Mail' → 'Other (custom name)'")
        print("   - Copy the 16-character password WITHOUT spaces")
        print("3. Update GMAIL_APP_PASSWORD in Replit Secrets")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()