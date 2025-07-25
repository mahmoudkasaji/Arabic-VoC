# Gmail Integration Setup Guide

## Current Status

✅ **Gmail Service Configured**: The system has been configured with Gmail credentials
❌ **Connection Failed**: Authentication error detected - credentials need verification

## Problem Diagnosis

The error message indicates:
```
(535, b'5.7.8 Username and Password not accepted. For more information, go to\n5.7.8  https://support.google.com/mail/?p=BadCredentials ada2fe7eead31-4fa46d31713sm81163137.7 - gsmtp')
```

This typically means:
1. **App Password Issue**: The Gmail App Password is incorrect or expired
2. **2FA Not Enabled**: Gmail requires 2-Factor Authentication for App Passwords
3. **Account Settings**: Less secure app access might be disabled

## Step-by-Step Solution

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the setup process to enable 2FA
4. **This is required** - App Passwords won't work without 2FA

### Step 2: Generate Gmail App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **App passwords**
3. Select **Mail** as the app type
4. Select **Other (custom name)** and enter "Voice of Customer Platform"
5. Click **Generate** 
6. **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)

### Step 3: Update Replit Secrets
The App Password should be entered **without spaces**:
- ✅ Correct: `abcdabcdabcdabcd`
- ❌ Wrong: `abcd abcd abcd abcd`

### Step 4: Verify Account Settings
1. Ensure the Gmail account is active and accessible
2. Check that IMAP/SMTP is enabled in Gmail settings
3. Verify no unusual security restrictions are in place

## Test the Integration

Visit the test page: [Gmail Test Interface](/gmail-test)

This page will:
- Show current configuration status
- Allow you to send test emails
- Provide real-time troubleshooting feedback

## Common Issues & Solutions

### Issue: "Username and Password not accepted"
**Solution**: Regenerate the App Password and ensure it's entered without spaces

### Issue: "Less secure app access"
**Solution**: Use App Passwords instead of the regular Gmail password (this IS the secure method)

### Issue: "2FA required" 
**Solution**: Enable 2-Factor Authentication on the Google Account first

### Issue: "Account locked or suspended"
**Solution**: Check Gmail account status and any security notifications

## Professional Email Template

Once configured, surveys will be sent with this Arabic template:

**Subject**: استطلاع رأي: [Survey Title]

**Body**:
```
السلام عليكم ورحمة الله وبركاته،

يسعدنا دعوتكم للمشاركة في استطلاع رأي مهم حول: [Survey Title]

للمشاركة في الاستطلاع، يرجى الضغط على الرابط التالي:
[Survey Link]

نقدر وقتكم الثمين ومشاركتكم معنا في تحسين خدماتنا.

مع أطيب التحيات،
فريق منصة صوت العميل
```

## Next Steps

1. **Verify 2FA**: Ensure 2-Factor Authentication is enabled
2. **Regenerate App Password**: Create a fresh 16-character App Password
3. **Update Secrets**: Enter the new App Password in Replit Secrets (no spaces)
4. **Test Connection**: Use the Gmail test interface to verify functionality

Once Gmail is working, you can:
- Send professional Arabic survey invitations
- Track delivery status and results
- Maintain your sender reputation through Gmail's infrastructure
- Scale to thousands of survey invitations per day

## Support Resources

- [Google App Passwords Help](https://support.google.com/accounts/answer/185833)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [2-Step Verification Setup](https://support.google.com/accounts/answer/185839)