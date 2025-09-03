# TalentSync Email Integration

A React-based email integration system for scheduling interviews and sending personalized emails to candidates.

## Features

- **React Frontend**: Modern web interface for managing interview scheduling
- **Email Template Generation**: Uses React components to generate HTML emails
- **FastAPI Backend**: Python-based API for email processing and database integration
- **Server-Side Rendering**: React components are rendered server-side for email generation

## Technology Stack

- **Frontend**: React 18, Material-UI
- **Backend**: FastAPI, Python 3
- **Email Generation**: React Server-Side Rendering (Node.js)
- **Database**: MongoDB
- **Email Service**: SMTP (Gmail)

## Project Structure

```
├── src/                    # React frontend source
│   ├── App.js             # Main React application
│   ├── EmailTemplate.js   # React email template component
│   ├── emailUtils.js      # Email utility functions
│   └── index.js          # React entry point
├── public/                # Static assets
├── generateEmail.js       # Node.js script for email generation
├── main.py               # FastAPI backend
├── requirements.txt      # Python dependencies
└── package.json          # Node.js dependencies
```

## Setup

### 1. Install Dependencies

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Install Node.js dependencies:
```bash
npm install
```

### 2. Environment Variables

Create a `.env` file with:
```
MONGODB_URI=your_mongodb_connection_string
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 3. Build React Frontend

```bash
npm run build
```

### 4. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## How It Works

1. **Email Template**: The `EmailTemplate.js` React component defines the email structure
2. **Server-Side Rendering**: The `generateEmail.js` script renders React components to HTML
3. **Python Integration**: The FastAPI backend calls the Node.js script to generate emails
4. **Email Sending**: Generated HTML is sent via SMTP to candidates

## API Endpoints

- `GET /` - Serves the React frontend
- `POST /schedule-interviews/` - Schedules interviews and sends emails

## Email Generation Flow

1. Python backend calls `node generateEmail.js <name> <time>`
2. Node.js renders the React EmailTemplate component
3. Resulting HTML is returned to Python
4. Python sends the HTML email via SMTP

## Development

To run in development mode:

```bash
# Start React development server
npm start

# Start FastAPI backend (in another terminal)
uvicorn main:app --reload
```

## Converting from HTML to React

This project demonstrates converting from hardcoded HTML strings to a React-based template system:

**Before (HTML strings in Python):**
```python
html = f"""
<html>
  <body>
    <p>Dear {candidate['name']},</p>
    <!-- ... more HTML ... -->
  </body>
</html>
"""
```

**After (React components):**
```javascript
const EmailTemplate = ({ candidateName, interviewTime }) => {
  return (
    <div>
      <p>Dear {candidateName},</p>
      {/* ... more JSX ... */}
    </div>
  );
};
```

This approach provides better maintainability, reusability, and allows for complex templating logic.