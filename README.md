# Waitlist Form Backend

A simple FastAPI backend service that handles waitlist form submissions and stores them in a JSON file.

## Features

- Form submission endpoint (`POST /submit`)
- Data validation using Pydantic
- JSON file storage
- CORS support
- Health check endpoint
- Error handling and logging

## Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the development server:

```bash
uvicorn main:app --reload
```

## API Endpoints

### POST /submit

Submit waitlist form data.

Request body:

```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "company": "string",
  "role": "string",
  "team_size": "string",
  "challenges": ["string"]
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

5. Deploy!

## Data Storage

Submissions are stored in a `submissions.json` file in the project root. Each submission includes:

- All form fields
- Timestamp of submission

## Security Notes

- CORS is currently set to allow all origins (`*`). In production, this should be restricted to specific domains.
- Consider adding rate limiting for the `/submit` endpoint in production.
- The `submissions.json` file should be backed up regularly in production.

## Project Structure

```
.
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── render.yaml         # Render configuration
├── Procfile           # Process file for Render
└── README.md          # This file
```
