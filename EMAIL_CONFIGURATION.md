# Email Configuration for Password Reset System

This document explains how to configure email sending for the OTP-based password reset feature.

## Overview

The password reset system supports multiple email providers through environment variables. If email is not configured, OTP codes will be printed to the console for testing purposes.

## Quick Start - Testing Without Email

For testing, you don't need to configure email. The OTP code will be displayed in the console logs:
1. User requests password reset
2. Check the Flask console logs for the OTP code
3. Use that code to verify and reset password

## Email Provider Options

### Option 1: Gmail (Recommended for Testing)

**Requirements:**
- A Gmail account
- App-specific password (2FA must be enabled)

**Setup Steps:**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App passwords
3. Generate an app password for "Mail"
4. Add these environment variables in Replit Secrets:

```
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SENDER_EMAIL=your-email@gmail.com
```

### Option 2: SendGrid (Recommended for Production)

**Requirements:**
- SendGrid account (free tier available)
- SendGrid API key

**Setup Steps:**
1. Sign up at https://sendgrid.com
2. Create an API key with "Mail Send" permissions
3. Set up Replit integration or add these environment variables:

```
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDER_EMAIL=verified-sender@yourdomain.com
```

Note: SendGrid requires sender verification. Verify your email in SendGrid dashboard.

### Option 3: Resend (Modern Alternative)

**Requirements:**
- Resend account
- Resend API key

**Setup Steps:**
1. Sign up at https://resend.com
2. Get your API key from dashboard
3. Use Replit's Resend integration or configure manually:

```
EMAIL_PROVIDER=resend
RESEND_API_KEY=your-resend-api-key
SENDER_EMAIL=onboarding@resend.dev
```

### Option 4: Generic SMTP (Any Provider)

For any SMTP email provider:

```
EMAIL_PROVIDER=smtp
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SENDER_EMAIL=noreply@yourcompany.com
```

## Adding Environment Variables in Replit

### Method 1: Secrets Panel (Recommended)
1. Click on "Tools" in the left sidebar
2. Select "Secrets"
3. Add each variable as a new secret:
   - Key: `SMTP_HOST`
   - Value: `smtp.gmail.com`
4. Repeat for all variables listed above

### Method 2: .env File (Development Only)
1. Create a `.env` file in your project root
2. Add your variables:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-password
   SENDER_EMAIL=your-email@gmail.com
   ```
3. **Never commit this file to Git!** (It's in .gitignore)

## How Password Reset Works

### Step 1: Request Reset (`/forgot_password`)
1. User enters their username
2. System looks up email from `registration_requests` table
3. Generates 6-digit OTP code using `secrets` module
4. Saves OTP to `password_reset_tokens` table (expires in 15 minutes)
5. Sends HTML email with OTP code

### Step 2: Verify OTP (`/verify_otp`)
1. User enters OTP code from email
2. System validates code hasn't expired or been used
3. If valid, proceeds to password reset

### Step 3: Reset Password (`/reset_password_with_otp`)
1. User enters new password (min 6 characters)
2. Password is hashed using `werkzeug.security`
3. Updates both `users` and `engineers` tables
4. Marks OTP as used
5. Redirects to login

## Security Features

✅ **OTP Expiration**: Codes expire after 15 minutes
✅ **One-Time Use**: Each OTP can only be used once
✅ **Secure Generation**: Uses Python `secrets` module for cryptographic randomness
✅ **Password Hashing**: Passwords encrypted immediately with werkzeug.security
✅ **Session Protection**: Reset flow tracked via Flask sessions
✅ **HTML Emails**: Professional, branded email templates

## Troubleshooting

### OTP Email Not Received

**Check Console Logs:**
```
grep "OTP" /tmp/logs/Flask_App*.log
```

If email credentials aren't configured, you'll see:
```
WARNING: Email credentials not configured. OTP email not sent.
Debug: OTP for username (email@example.com): 123456
```

**Solution:** Copy the OTP from console and use it to verify

### SMTP Authentication Failed

**Common Issues:**
- Gmail: Use app password, not regular password
- SendGrid: Username must be exactly `apikey`
- Wrong credentials: Double-check SMTP_USERNAME and SMTP_PASSWORD

### User Has No Email Address

**Error:** "No email address registered for user"

**Solution:** Users must register through the public registration form (`/register`) which captures email addresses. Alternatively, admin can manually add email to `registration_requests` table.

## Email Template Customization

The OTP email template is in `app.py` in the `send_otp_email()` function. To customize:

1. Edit the `html_body` variable for visual changes
2. Edit the `text_body` variable for plain text version
3. Modify subject line in `msg['Subject']`

## Database Schema

### password_reset_tokens Table

```sql
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Testing the System

### Test Without Email Setup:
1. Go to `/forgot_password`
2. Enter any registered username
3. Check Flask console for OTP: `grep "Debug: OTP" logs`
4. Go to `/verify_otp`
5. Enter the OTP from console
6. Set new password

### Test With Email Setup:
1. Ensure environment variables are set
2. Restart the Flask workflow
3. Go to `/forgot_password`
4. Enter username
5. Check your email inbox for OTP
6. Complete the reset process

## Production Recommendations

For production deployment:

1. **Use Professional Email Provider:**
   - SendGrid (99.9% deliverability)
   - AWS SES (cost-effective at scale)
   - Mailgun (reliable, developer-friendly)

2. **Set Environment Variables in Replit Secrets:**
   - Never use .env in production
   - Use Replit's Secrets panel

3. **Monitor Email Delivery:**
   - Check provider dashboard for bounces
   - Monitor OTP usage in database

4. **Consider Rate Limiting:**
   - Limit OTP requests per user (3 per hour)
   - Add CAPTCHA for forgot password page

## Support

If you need help:
1. Check Flask console logs: `refresh_all_logs` tool
2. Query database: `SELECT * FROM password_reset_tokens ORDER BY created_at DESC LIMIT 10`
3. Test email manually using Python:
   ```python
   from app import send_otp_email
   send_otp_email('test@example.com', '123456', 'testuser')
   ```

---

**Created:** 2025-10-29
**System:** CRM and Presales Monitoring System
**Feature:** Password Reset with OTP via Email
