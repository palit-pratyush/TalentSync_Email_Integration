from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()

# MongoDB setup (base client)
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in environment variables")

client = MongoClient(MONGODB_URI)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sender details from environment variables
sender_email = os.getenv("SENDER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
if not sender_email or not email_password:
    raise ValueError("SENDER_EMAIL or EMAIL_PASSWORD not set in environment variables")

# Pydantic model for request validation
class ScheduleRequest(BaseModel):
    database_name: str
    collection_name: str

# Generate time slots (9:00 AM to 5:00 PM IST, 30-min intervals)
def generate_time_slots(start_date):
    slots = []
    current_time = datetime(start_date.year, start_date.month, start_date.day, 9, 0)  # 9:00 AM IST
    end_time = datetime(start_date.year, start_date.month, start_date.day, 17, 0)  # 5:00 PM IST
    while current_time <= end_time:
        slots.append(current_time.strftime("%Y-%m-%d %H:%M IST"))
        current_time += timedelta(minutes=30)
    return slots

# Schedule interviews and send emails
@app.post("/schedule-interviews/")
async def schedule_interviews(request: ScheduleRequest):
    try:
        # Connect to the specified database and collection
        db = client[request.database_name]
        candidates_collection = db[request.collection_name]

        # Fetch all candidates sorted by RANK
        candidates = list(candidates_collection.find().sort("RANK", 1))
        if not candidates:
            logger.warning(f"No candidates found in {request.database_name}.{request.collection_name}.")
            return {"message": f"No candidates found in {request.database_name}.{request.collection_name} to schedule interviews."}

        logger.info(f"Found candidates: {[cand['NAME'] for cand in candidates]}")

        # Calculate start date (2 days from now, skipping weekends)
        start_date = datetime.now() + timedelta(days=2)
        while start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            start_date += timedelta(days=1)

        available_slots = generate_time_slots(start_date)
        slot_index = 0
        current_date = start_date
        scheduled_emails = []

        # Assign slots and send emails
        for candidate in candidates:
            if slot_index >= len(available_slots):
                current_date += timedelta(days=1)
                while current_date.weekday() >= 5:  # Skip weekends
                    current_date += timedelta(days=1)
                available_slots = generate_time_slots(current_date)
                slot_index = 0

            interview_time = available_slots[slot_index]
            slot_index += 1

            # Create message template
            subject = "TalentSync Interview Schedule"
            text = f"This is your interview schedule from TalentSync. Your interview is scheduled for {interview_time}."
            html = f"""
            <html>
              <body>
                <p>Dear {candidate['NAME']},</p>
                <p>{text}</p>
                <p>Please be prepared and join the interview at the scheduled time. Details will follow. Use the following link of chatbot for further queries: https://chatbot-ui-five-cyan-56.vercel.app/</p>
                <p>Best regards,<br>TalentSync Team</p>
              </body>
            </html>
            """

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = candidate["EMAIL"]

            part = MIMEText(html, "html")
            message.attach(part)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, email_password)
                    server.sendmail(sender_email, candidate["EMAIL"], message.as_string())
                logger.info(f"Email sent successfully to {candidate['NAME']} at {candidate['EMAIL']} for {interview_time}")
                scheduled_emails.append({
                    "name": candidate["NAME"],
                    "email": candidate["EMAIL"],
                    "interview_time": interview_time
                })
            except Exception as e:
                logger.error(f"Failed to send email to {candidate['NAME']} at {candidate['EMAIL']}: {str(e)}")

        return {"message": f"Interviews scheduled and emails sent for {request.database_name}.{request.collection_name}", "scheduled": scheduled_emails}

    except Exception as e:
        logger.error(f"Error scheduling interviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule interviews: {str(e)}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
