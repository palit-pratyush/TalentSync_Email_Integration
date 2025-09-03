import React from 'react';

const EmailTemplate = ({ candidateName, interviewTime }) => {
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '0 auto' }}>
      <p>Dear {candidateName},</p>
      <p>
        We are pleased to inform you that your interview with NeonAI has been scheduled for {interviewTime}.
      </p>
      <p>
        Please ensure you are prepared and join the interview at the scheduled time. 
        Further details regarding the interview process will be provided soon.
      </p>
      <p>
        For any questions or assistance, you may reach out via our chatbot:{' '}
        <a 
          href="https://chatbot-ui-five-cyan-56.vercel.app/" 
          style={{ color: '#0066cc', textDecoration: 'none' }}
        >
          TalentSync Chatbot
        </a>
        .
      </p>
      <p>We look forward to speaking with you.</p>
      <p>
        Best regards,<br />
        The NeonAI Team
      </p>
    </div>
  );
};

export default EmailTemplate;