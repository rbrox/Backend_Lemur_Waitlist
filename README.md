# Waitlist Form Backend

A simple FastAPI backend service that handles waitlist form submissions and stores them in a JSON file.

## Features

- Form submission endpoint (`POST /submit`)
- Data validation using Pydantic
- JSON file storage
- CORS support
- Health check endpoint
- Error handling and logging
- **Automated thank you emails** with personalized messages
- **Duplicate email detection**
- **Asynchronous email sending** (non-blocking)
- **Beautiful HTML email templates**

## Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your email credentials (see EMAIL_SETUP.md for detailed instructions)
```

3. Run the development server:

```bash
uvicorn main:app --reload
```

📧 **For email functionality**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed email configuration instructions.

## API Endpoints

### POST /submit

Submit waitlist form data.

Request body:

```json
{
  "email": "string",
  "name": "string (optional)"
}
```

Example:
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

### GET /submissions

Get all submissions.

### GET /health

Health check endpoint.

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:

   - **Name**: waitlist-api (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11.0

4. Add the following environment variables in Render dashboard:

   - `PYTHON_VERSION`: 3.11.0
   - `SMTP_USERNAME`: Your email address (e.g., your-email@gmail.com)
   - `SMTP_PASSWORD`: Your email app password (for Gmail, generate an App Password)
   - `FROM_EMAIL`: Email address to send from (usually same as SMTP_USERNAME)
   - `FROM_NAME`: Display name for emails (e.g., "Lemur Waitlist")

5. Deploy!

## Email Configuration

The application sends personalized thank you emails to users who join the waitlist. To enable email functionality:

### For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: Google Account → Security → 2-Step Verification → App passwords
3. Use your Gmail address as `SMTP_USERNAME` and the generated app password as `SMTP_PASSWORD`

### For other email providers:
- Update `SMTP_SERVER` and `SMTP_PORT` in the environment variables
- Use your email provider's SMTP settings

### Environment Variables:
- `SMTP_SERVER`: SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)
- `SMTP_USERNAME`: Your email address
- `SMTP_PASSWORD`: Your email password or app password
- `FROM_EMAIL`: Email address to send from
- `FROM_NAME`: Display name for outgoing emails

**Note**: If email credentials are not configured, the application will still work but won't send emails.

## Data Storage

Submissions are stored in a `submissions.json` file in the project root. Each submission includes:

- Email address
- Name (optional)
- Timestamp of submission
- Unique ID

## Security Notes

- CORS is currently set to allow all origins (`*`). In production, this should be restricted to specific domains.
- Consider adding rate limiting for the `/submit` endpoint in production.
- The `submissions.json` file should be backed up regularly in production.

## Project Structure

```
.
├── main.py              # Main application file
├── email_templates.py   # Email template functions
├── requirements.txt     # Python dependencies
├── render.yaml         # Render configuration
├── Procfile           # Process file for Render
├── submissions.json    # Waitlist submissions (auto-generated)
└── README.md          # This file
```
