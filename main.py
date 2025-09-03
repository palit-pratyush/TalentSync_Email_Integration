from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import subprocess
import json

# Initialize FastAPI app
app = FastAPI()

# CORS setup: allow all HTTPS and localhost ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in environment variables")

client = MongoClient(MONGODB_URI)
db = client["selected_db"]
candidates_collection = db["selected"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sender details from environment variables
sender_email = os.getenv("SENDER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
if not sender_email or not email_password:
    raise ValueError("SENDER_EMAIL or EMAIL_PASSWORD not set in environment variables")

# Generate time slots (9:00 AM to 5:00 PM IST, 30-min intervals)
def generate_time_slots(start_date):
    slots = []
    current_time = datetime(start_date.year, start_date.month, start_date.day, 9, 0)
    end_time = datetime(start_date.year, start_date.month, start_date.day, 17, 0)
    while current_time <= end_time:
        slots.append(current_time.strftime("%Y-%m-%d %H:%M IST"))
        current_time += timedelta(minutes=30)
    return slots

# Generate email HTML using React component
def generate_email_html(candidate_name, interview_time):
    try:
        # Call the Node.js script to generate HTML from React component
        result = subprocess.run(
            ['node', 'generateEmail.js', candidate_name, interview_time],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.error(f"Error generating email HTML: {result.stderr}")
            # Fallback to simple HTML if React generation fails
            return f"""
            <html>
              <body>
                <p>Dear {candidate_name},</p>
                <p>We are pleased to inform you that your interview with NeonAI has been scheduled for {interview_time}.</p>
                <p>Please ensure you are prepared and join the interview at the scheduled time. Further details regarding the interview process will be provided soon.</p>
                <p>For any questions or assistance, you may reach out via our chatbot: <a href="https://chatbot-ui-five-cyan-56.vercel.app/">TalentSync Chatbot</a>.</p>
                <p>We look forward to speaking with you.</p>
                <p>Best regards,<br>
                The NeonAI Team</p>
              </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Exception generating email HTML: {str(e)}")
        # Fallback to simple HTML
        return f"""
        <html>
          <body>
            <p>Dear {candidate_name},</p>
            <p>We are pleased to inform you that your interview with NeonAI has been scheduled for {interview_time}.</p>
            <p>Please ensure you are prepared and join the interview at the scheduled time. Further details regarding the interview process will be provided soon.</p>
            <p>For any questions or assistance, you may reach out via our chatbot: <a href="https://chatbot-ui-five-cyan-56.vercel.app/">TalentSync Chatbot</a>.</p>
            <p>We look forward to speaking with you.</p>
            <p>Best regards,<br>
            The NeonAI Team</p>
          </body>
        </html>
        """

# Schedule interviews and send emails
@app.post("/schedule-interviews/")
async def schedule_interviews():
    try:
        candidates = list(candidates_collection.find().sort("rank", 1))
        if not candidates:
            logger.warning("No candidates found in the database.")
            return {"message": "No candidates found to schedule interviews."}

        logger.info(f"Found candidates: {[cand['name'] for cand in candidates]}")

        # Calculate start date (2 days from now, skipping weekends)
        start_date = datetime.now() + timedelta(days=2)
        while start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            start_date += timedelta(days=1)

        available_slots = generate_time_slots(start_date)
        slot_index = 0
        current_date = start_date
        scheduled_emails = []

        for candidate in candidates:
            if slot_index >= len(available_slots):
                current_date += timedelta(days=1)
                while current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                available_slots = generate_time_slots(current_date)
                slot_index = 0

            interview_time = available_slots[slot_index]
            slot_index += 1

            # Create email content using React component
            subject = "Interview Call from NeonAI!!"
            html = generate_email_html(candidate['name'], interview_time)

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = candidate["email"]

            part = MIMEText(html, "html")
            message.attach(part)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, email_password)
                    server.sendmail(sender_email, candidate["email"], message.as_string())
                logger.info(f"Email sent to {candidate['name']} ({candidate['email']}) for {interview_time}")
                scheduled_emails.append({
                    "name": candidate["name"],
                    "email": candidate["email"],
                    "interview_time": interview_time
                })
            except Exception as e:
                logger.error(f"Failed to send email to {candidate['name']} ({candidate['email']}): {str(e)}")

        return {
            "message": "Interviews scheduled and emails sent",
            "scheduled": scheduled_emails
        }

    except Exception as e:
        logger.error(f"Error scheduling interviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule interviews: {str(e)}")

# Serve React frontend (if build exists)
@app.get("/")
async def serve_frontend():
    try:
        return FileResponse('build/index.html')
    except:
        return {"message": "TalentSync Email Integration API", "frontend": "Run 'npm run build' to build React frontend"}

# Mount static files for React build
if os.path.exists("build"):
    app.mount("/static", StaticFiles(directory="build/static"), name="static")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
