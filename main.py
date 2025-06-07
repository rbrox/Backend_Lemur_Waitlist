from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import logging
from datetime import datetime
from pathlib import Path
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from concurrent.futures import ThreadPoolExecutor
from email_templates import get_welcome_email_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FROM_NAME = os.getenv("FROM_NAME", "Lemur Waitlist")

app = FastAPI(
    title="Waitlist API",
    description="API for handling waitlist form submissions",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Added DELETE method
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length"],
    max_age=600,
)

# Thread pool for async email sending
email_executor = ThreadPoolExecutor(max_workers=3)

# Pydantic model for form validation
class WaitlistSubmission(BaseModel):
    email: str
    name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }

def create_thank_you_email(user_email: str, user_name: Optional[str] = None) -> MIMEMultipart:
    """Create a personalized thank you email for waitlist registration."""

    # Get email template
    template = get_welcome_email_template(user_name)

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = template['subject']
    msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg['To'] = user_email

    # Add both text and HTML parts
    text_part = MIMEText(template['text'], 'plain')
    html_part = MIMEText(template['html'], 'html')

    msg.attach(text_part)
    msg.attach(html_part)

    return msg

def send_email_sync(user_email: str, user_name: Optional[str] = None) -> bool:
    """Send thank you email synchronously."""
    try:
        # Check if email configuration is available
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("Email credentials not configured, skipping email send")
            return False

        # Create email
        msg = create_thank_you_email(user_email, user_name)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Thank you email sent successfully to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")
        return False

async def send_thank_you_email(user_email: str, user_name: Optional[str] = None) -> bool:
    """Send thank you email asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(email_executor, send_email_sync, user_email, user_name)

# Create submissions.json if it doesn't exist
SUBMISSIONS_FILE = Path("submissions.json")
if not SUBMISSIONS_FILE.exists():
    SUBMISSIONS_FILE.write_text(json.dumps([], indent=2))

def read_submissions() -> List[dict]:
    """Read submissions from JSON file with error handling"""
    try:
        return json.loads(SUBMISSIONS_FILE.read_text())
    except json.JSONDecodeError:
        logger.error("Invalid JSON in submissions file, resetting to empty list")
        SUBMISSIONS_FILE.write_text(json.dumps([], indent=2))
        return []
    except Exception as e:
        logger.error(f"Error reading submissions file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to read submissions")

def write_submissions(submissions: List[dict]) -> None:
    """Write submissions to JSON file with error handling"""
    try:
        SUBMISSIONS_FILE.write_text(json.dumps(submissions, indent=2))
    except Exception as e:
        logger.error(f"Error writing to submissions file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save submission")

@app.get("/submissions", response_model=List[dict])
async def get_submissions() -> List[dict]:
    """Get all waitlist submissions."""
    return read_submissions()

@app.get("/download-submissions")
async def download_submissions():
    """Download all submissions as a JSON file."""
    try:
        submissions = read_submissions()
        return JSONResponse(
            content=submissions,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    except Exception as e:
        logger.error(f"Failed to prepare download: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to prepare download")

@app.post("/submit", response_model=dict)
async def submit(submission: WaitlistSubmission) -> dict:
    """Handle waitlist form submissions and store in JSON file."""
    try:
        logger.info(f"Received submission from: {submission.email} (name: {submission.name})")

        submissions = read_submissions()

        # Check for duplicate email
        existing_emails = [sub.get("email") for sub in submissions]
        if submission.email in existing_emails:
            logger.warning(f"Duplicate email submission attempted: {submission.email}")
            return {
                "status": "info",
                "message": "You're already on our waitlist! We'll be in touch soon."
            }

        # Calculate the next ID (1-based indexing)
        next_id = len(submissions) + 1

        submission_data = {
            "id": next_id,
            "email": submission.email,
            "name": submission.name,
            "timestamp": datetime.now().isoformat()
        }

        # Append to the end of the list
        submissions.append(submission_data)
        write_submissions(submissions)

        # Send thank you email asynchronously
        email_sent = False
        try:
            email_sent = await send_thank_you_email(submission.email, submission.name)
        except Exception as email_error:
            logger.error(f"Email sending failed for {submission.email}: {str(email_error)}")
            # Don't fail the registration if email fails

        logger.info(f"Successfully added submission for {submission.email} (email sent: {email_sent})")

        # Customize response message based on name
        if submission.name:
            message = f"Thank you, {submission.name}, for joining our waitlist! Check your email for a welcome message."
        else:
            message = "Thank you for joining our waitlist! Check your email for a welcome message."

        if not email_sent:
            message += " (Note: Welcome email could not be sent, but you're successfully registered!)"

        return {
            "status": "success",
            "message": message,
            "email_sent": email_sent
        }

    except Exception as e:
        logger.error(f"Failed to process submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/submissions/{submission_id}")
async def delete_submission(submission_id: int) -> dict:
    """Delete a submission by its ID."""
    try:
        submissions = read_submissions()
        
        # Find the submission with the given ID
        submission_index = next(
            (index for index, sub in enumerate(submissions) if sub["id"] == submission_id),
            None
        )
        
        if submission_index is None:
            raise HTTPException(status_code=404, detail=f"Submission with ID {submission_id} not found")
        
        # Remove the submission
        deleted_submission = submissions.pop(submission_index)
        
        # Update IDs for remaining submissions
        for i, submission in enumerate(submissions, start=1):
            submission["id"] = i
        
        # Save the updated submissions
        write_submissions(submissions)
        
        logger.info(f"Successfully deleted submission with ID {submission_id}")
        return {
            "status": "success",
            "message": f"Submission {submission_id} deleted successfully",
            "deleted_submission": deleted_submission
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete submission")

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "port": PORT,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT} with allowed origins: *")
    uvicorn.run(app, host="0.0.0.0", port=PORT)