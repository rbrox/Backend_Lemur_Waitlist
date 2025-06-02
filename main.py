from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Waitlist API",
    description="API for handling waitlist form submissions",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Limit in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for form validation
class WaitlistSubmission(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    role: str
    team_size: str
    challenges: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "company": "Acme Corp",
                "role": "Product Manager",
                "team_size": "10-50",
                "challenges": ["Meeting Overload", "Calendar Management"]
            }
        }

# Create submissions.json if it doesn't exist
SUBMISSIONS_FILE = Path("submissions.json")
if not SUBMISSIONS_FILE.exists():
    # Initialize with some example data
    example_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "company": "Acme Corp",
            "role": "Product Manager",
            "team_size": "10-50",
            "challenges": ["Meeting Overload", "Calendar Management"],
            "timestamp": datetime.now().isoformat()
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "company": "TechStart",
            "role": "Engineering Manager",
            "team_size": "50-200",
            "challenges": ["Team Coordination", "Project Planning"],
            "timestamp": datetime.now().isoformat()
        }
    ]
    SUBMISSIONS_FILE.write_text(json.dumps(example_data, indent=2))

@app.get("/submissions", response_model=List[dict])
async def get_submissions() -> List[dict]:
    """
    Get all waitlist submissions.
    
    Returns:
        List[dict]: List of all submissions with their details
    """
    try:
        submissions = json.loads(SUBMISSIONS_FILE.read_text())
        return submissions
    except Exception as e:
        logger.error(f"Failed to read submissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to read submissions")

@app.post("/submit", response_model=dict)
async def submit(submission: WaitlistSubmission) -> dict:
    """
    Handle waitlist form submissions and store in JSON file.
    
    Args:
        submission: WaitlistSubmission model containing form data
        
    Returns:
        dict: Status response
        
    Raises:
        HTTPException: If submission fails or data is invalid
    """
    try:
        # Prepare submission data
        submission_data = {
            "first_name": submission.first_name,
            "last_name": submission.last_name,
            "email": submission.email,
            "company": submission.company,
            "role": submission.role,
            "team_size": submission.team_size,
            "challenges": submission.challenges,
            "timestamp": datetime.now().isoformat()
        }
        
        # Read existing submissions
        submissions = json.loads(SUBMISSIONS_FILE.read_text())
        
        # Append new submission
        submissions.append(submission_data)
        
        # Write back to file
        SUBMISSIONS_FILE.write_text(json.dumps(submissions, indent=2))
        
        logger.info(f"Successfully added submission for {submission.email}")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Failed to process submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "healthy"} 