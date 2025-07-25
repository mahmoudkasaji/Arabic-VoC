# Gmail App Password Setup - Step by Step Guide

## Step 1: Enable 2-Factor Authentication (Required)

1. **Go to your Google Account**
   - Visit: https://myaccount.google.com
   - Or click your profile picture in Gmail → "Manage your Google Account"

2. **Navigate to Security**
   - Click "Security" in the left sidebar
   - Look for the "Signing in to Google" section

3. **Enable 2-Step Verification**
   - Click "2-Step Verification"
   - If it says "Off", click to turn it on
   - Follow the setup process (usually involves your phone number)
   - **This step is mandatory** - App Passwords won't appear without 2FA enabled

## Step 2: Generate App Password

1. **Return to Security Page**
   - Go back to https://myaccount.google.com/security
   - Look for "Signing in to Google" section again

2. **Find App Passwords**
   - You should now see "App passwords" option
   - If you don't see it, 2-Step Verification might not be fully enabled yet

3. **Click "App passwords"**
   - You may need to enter your regular Gmail password again

4. **Generate New App Password**
   - Select app: Choose "Mail"
   - Select device: Choose "Other (custom name)"
   - Enter name: Type "Voice of Customer Platform"
   - Click "Generate"

5. **Copy the Password**
   - Google will show a 16-character password like: `abcd efgh ijkl mnop`
   - **Copy ALL 16 characters**
   - **Remove any spaces** when entering into Replit

## Step 3: Update Replit Secrets

1. **In your Replit project**
   - Go to the "Secrets" tab (lock icon in sidebar)
   - Find `GMAIL_APP_PASSWORD`
   - Update it with the 16-character password (no spaces)
   - Example: `abcdefghijklmnop`

## Common Issues & Solutions

### Issue: "App passwords" option doesn't appear
**Solution**: 2-Step Verification isn't fully enabled. Go back and complete the 2FA setup.

### Issue: "This setting is not available for your account"
**Solution**: Your account might have restrictions. Try:
- Using a personal Gmail account (not work/school)
- Waiting a few hours after enabling 2FA
- Checking if your account has any security restrictions

### Issue: Password still doesn't work after setup
**Solution**: 
- Make sure you copied all 16 characters
- Remove any spaces from the password
- Try regenerating a new App Password

### Issue: 2-Factor Authentication seems complicated
**Solution**: The simplest 2FA method is SMS to your phone number. Google will walk you through it.

## What Happens After Setup

Once the App Password is working:
- Survey emails will be sent from your Gmail account
- Professional Arabic email templates will be used
- You'll maintain your Gmail sender reputation
- No per-email costs (unlike SendGrid)
- Full delivery tracking and status monitoring

## Need Help?

If you get stuck at any step, let me know exactly where you are in the process and what you're seeing on screen. I can provide more specific guidance.