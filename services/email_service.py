import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from cryptography.fernet import Fernet

class EmailService:
    def __init__(self, encryption_key: str):
        """
        Initialize Email Service with encryption for sensitive data.
        """
        self.encryption_key = encryption_key
        self.cipher = Fernet(encryption_key)

    def load_user_emails(self, user_file: str) -> list:
        """
        Load and decrypt user email accounts from the user's JSON file.
        
        Args:
            user_file (str): Path to the user's data file.
        
        Returns:
            list: A list of email account dictionaries.
        """
        try:
            with open(user_file, "r") as file:
                user_data = json.load(file)
            encrypted_emails = user_data.get("emails", [])
            return [
                {
                    "address": self.cipher.decrypt(email["address"].encode()).decode(),
                    "password": self.cipher.decrypt(email["password"].encode()).decode(),
                }
                for email in encrypted_emails
            ]
        except Exception as e:
            print(f"Error loading user emails: {e}")
            return []

    def send_email(self, from_email: dict, to_email: str, subject: str, body: str) -> str:
        """
        Send an email using the selected account.

        Args:
            from_email (dict): Dictionary with 'address' and 'password'.
            to_email (str): Recipient's email address.
            subject (str): Subject of the email.
            body (str): Body of the email.

        Returns:
            str: Success or error message.
        """
        try:
            # Determine the SMTP server based on the email domain
            email_domain = from_email["address"].split("@")[-1]
            if "gmail.com" in email_domain:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
            elif "outlook.com" in email_domain or "hotmail.com" in email_domain or "live.com" in email_domain:
                smtp_server = "smtp.office365.com"
                smtp_port = 587
            elif "yahoo.com" in email_domain:
                smtp_server = "smtp.mail.yahoo.com"
                smtp_port = 465
            else:
                return f"Unsupported email provider: {email_domain}"

            # Set up the email
            message = MIMEMultipart()
            message["From"] = from_email["address"]
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(from_email["address"], from_email["password"])
                server.send_message(message)

            return "Email sent successfully!"
        except Exception as e:
            return f"Error sending email: {e}"

