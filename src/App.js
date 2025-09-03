import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Box, 
  Alert,
  CircularProgress 
} from '@mui/material';
import axios from 'axios';
import EmailTemplate from './EmailTemplate';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleScheduleInterviews = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:8000/schedule-interviews/');
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to schedule interviews');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        TalentSync Email Integration
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Interview Scheduler
        </Typography>
        <Typography variant="body1" paragraph>
          Click the button below to schedule interviews for all candidates in the database.
          This will automatically generate time slots and send personalized email invitations.
        </Typography>
        
        <Button
          variant="contained"
          size="large"
          onClick={handleScheduleInterviews}
          disabled={loading}
          sx={{ mr: 2 }}
        >
          {loading ? <CircularProgress size={24} sx={{ mr: 1 }} /> : null}
          Schedule Interviews
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Scheduling Results
          </Typography>
          <Typography variant="body2" paragraph>
            {result.message}
          </Typography>
          
          {result.scheduled && result.scheduled.length > 0 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Scheduled Interviews ({result.scheduled.length}):
              </Typography>
              {result.scheduled.map((candidate, index) => (
                <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Typography variant="body2">
                    <strong>{candidate.name}</strong> ({candidate.email})<br />
                    Interview Time: {candidate.interview_time}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Paper>
      )}

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Email Template Preview
        </Typography>
        <Typography variant="body2" paragraph color="text.secondary">
          This is how the email will look when sent to candidates:
        </Typography>
        <Box sx={{ border: '1px solid #ddd', p: 2, borderRadius: 1, bgcolor: 'white' }}>
          <EmailTemplate 
            candidateName="[Candidate Name]" 
            interviewTime="[Interview Date & Time]" 
          />
        </Box>
      </Paper>
    </Container>
  );
}

export default App;