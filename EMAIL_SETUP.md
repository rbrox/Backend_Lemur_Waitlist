# Email Setup Guide for Lemur Waitlist

This guide will help you configure email functionality for sending personalized thank you messages to waitlist subscribers.

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your email credentials (see detailed instructions below)

3. **Test the setup** by running the server and submitting a test registration

## Environment Variables Required

Your `.env` file should contain:

```env
# Server Configuration
PORT=8000
ENVIRONMENT=development

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Lemur Waitlist

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

## Email Provider Setup Instructions

### Gmail (Recommended)

1. **Enable 2-Factor Authentication:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password

3. **Update .env file:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-gmail@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   FROM_EMAIL=your-gmail@gmail.com
   FROM_NAME=Lemur Waitlist
   ```

### Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
FROM_NAME=Lemur Waitlist
```

### Yahoo Mail

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@yahoo.com
FROM_NAME=Lemur Waitlist
```

### Custom SMTP Server

```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Lemur Waitlist
```

## Testing Email Configuration

1. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Test with curl:**
   ```bash
   curl -X POST "http://localhost:8000/submit" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "name": "Test User"}'
   ```

3. **Check the logs** for email sending status

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - For Gmail: Make sure you're using an App Password, not your regular password
   - Check that 2FA is enabled

2. **"Connection refused"**
   - Verify SMTP_SERVER and SMTP_PORT are correct
   - Check firewall settings

3. **"Email not sent but no error"**
   - Check that SMTP_USERNAME and SMTP_PASSWORD are not empty
   - Verify the email credentials are correct

### Debug Mode:

Add this to your `.env` for more detailed logging:
```env
ENVIRONMENT=development
```

## Security Notes

- **Never commit your `.env` file** to version control
- Use App Passwords instead of regular passwords when possible
- Consider using environment-specific email addresses for different deployments
- For production, use a dedicated email service like SendGrid or AWS SES

## Production Deployment

For production on Render, set these environment variables in the Render dashboard instead of using a `.env` file:

- `SMTP_USERNAME`
- `SMTP_PASSWORD` 
- `FROM_EMAIL`
- `FROM_NAME`
- `SMTP_SERVER` (if different from Gmail)
- `SMTP_PORT` (if different from 587)
