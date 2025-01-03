import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailService:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, subject, message):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return "Email sent successfully."
        except Exception as e:
            return f"Failed to send email: {str(e)}"
