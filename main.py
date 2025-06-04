from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import json
import logging
from datetime import datetime
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

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

# Pydantic model for form validation
class WaitlistSubmission(BaseModel):
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

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
        logger.info(f"Received submission from: {submission.email}")
        
        submissions = read_submissions()
        
        # Calculate the next ID (1-based indexing)
        next_id = len(submissions) + 1
        
        submission_data = {
            "id": next_id,
            "email": submission.email,
            "timestamp": datetime.now().isoformat()
        }
        
        # Append to the end of the list
        submissions.append(submission_data)
        write_submissions(submissions)
        
        logger.info(f"Successfully added submission for {submission.email}")
        return {"status": "success", "message": "Thank you for joining our waitlist!"}
        
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