const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');

// React component definition in Node.js
const EmailTemplate = ({ candidateName, interviewTime }) => {
  return React.createElement('div', {
    style: { fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '0 auto' }
  }, [
    React.createElement('p', { key: 'greeting' }, `Dear ${candidateName},`),
    React.createElement('p', { key: 'intro' }, 
      `We are pleased to inform you that your interview with NeonAI has been scheduled for ${interviewTime}.`
    ),
    React.createElement('p', { key: 'instructions' }, 
      'Please ensure you are prepared and join the interview at the scheduled time. Further details regarding the interview process will be provided soon.'
    ),
    React.createElement('p', { key: 'chatbot' }, [
      'For any questions or assistance, you may reach out via our chatbot: ',
      React.createElement('a', {
        href: 'https://chatbot-ui-five-cyan-56.vercel.app/',
        style: { color: '#0066cc', textDecoration: 'none' },
        key: 'link'
      }, 'TalentSync Chatbot'),
      '.'
    ]),
    React.createElement('p', { key: 'closing' }, 'We look forward to speaking with you.'),
    React.createElement('p', { key: 'signature' }, [
      'Best regards,',
      React.createElement('br', { key: 'br' }),
      'The NeonAI Team'
    ])
  ]);
};

// Function to generate HTML
function generateEmailHTML(candidateName, interviewTime) {
  const emailComponent = React.createElement(EmailTemplate, {
    candidateName,
    interviewTime
  });
  
  const htmlContent = renderToStaticMarkup(emailComponent);
  
  return `
    <html>
      <body>
        ${htmlContent}
      </body>
    </html>
  `;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length !== 2) {
    console.error('Usage: node generateEmail.js <candidateName> <interviewTime>');
    process.exit(1);
  }
  
  const [candidateName, interviewTime] = args;
  const html = generateEmailHTML(candidateName, interviewTime);
  console.log(html);
}

module.exports = { generateEmailHTML };