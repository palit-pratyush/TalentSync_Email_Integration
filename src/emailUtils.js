import React from 'react';
import { renderToString } from 'react-dom/server';
import EmailTemplate from './EmailTemplate';

// Function to generate HTML email from React component
export const generateEmailHTML = (candidateName, interviewTime) => {
  const emailComponent = React.createElement(EmailTemplate, {
    candidateName,
    interviewTime
  });
  
  const htmlContent = renderToString(emailComponent);
  
  // Wrap in complete HTML structure for email
  return `
    <html>
      <body>
        ${htmlContent}
      </body>
    </html>
  `;
};

export default { generateEmailHTML };