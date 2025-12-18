# services/email_service.py
from __future__ import annotations

import os
import json
import smtplib
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional: cryptography for encrypted creds
try:
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # still usable without it (plaintext creds only)
    Fernet = None  # type: ignore

# Optional: Gmail API
try:
    from google.oauth2.credentials import Credentials  # type: ignore
    from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
    from googleapiclient.discovery import build  # type: ignore
except Exception:
    Credentials = None  # type: ignore
    InstalledAppFlow = None  # type: ignore
    build = None  # type: ignore

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class EmailService:
    """
    Unified email service:
      - SMTP send (supports plaintext creds or Fernet-encrypted creds)
      - Optional Gmail API read (unread inbox summaries)

    Encrypted creds:
      - Put a Fernet key in env JAICAT_EMAIL_KEY (urlsafe base64).
      - In your user json (default data/memory.json), store:
          {"emails": [{"address":"<Fernet str>","password":"<Fernet str>"}]}
        If not encrypted, plaintext values also work (not recommended).

    Gmail API:
      - Put OAuth client file at: config/credentials.json
      - Token will be saved to:   config/gmail_token.json
    """

    def __init__(
        self,
        user_file: str = "data/memory.json",
        fernet_env_key: str = "JAICAT_EMAIL_KEY",
        gmail_creds_path: str = "config/credentials.json",
        gmail_token_path: str = "config/gmail_token.json",
        default_from: Optional[Dict[str, str]] = None,
    ):
        self.user_file = user_file
        self.gmail_creds_path = gmail_creds_path
        self.gmail_token_path = gmail_token_path
        self._gmail = None  # lazy
        self._cipher = None

        key = os.getenv(fernet_env_key, "").strip()
        if key and Fernet:
            try:
                self._cipher = Fernet(key.encode("utf-8"))
            except Exception:
                self._cipher = None  # bad key; continue without decryption

        self.default_from = default_from

    # ------------------ credential loading ------------------

    def _maybe_decrypt(self, val: str) -> str:
        if not isinstance(val, str):
            return str(val)
        if self._cipher is None:
            return val
        try:
            return self._cipher.decrypt(val.encode("utf-8")).decode("utf-8")
        except Exception:
            # Not encrypted or wrong key — return original
            return val

    def load_user_emails(self) -> List[Dict[str, str]]:
        """
        Reads self.user_file (default: data/memory.json) and returns a list of {"address","password"} dicts.
        Works with plaintext or Fernet-encrypted strings.
        """
        try:
            with open(self.user_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        emails = data.get("emails", [])
        out: List[Dict[str, str]] = []
        for item in emails:
            try:
                addr = self._maybe_decrypt(item.get("address", ""))
                pwd = self._maybe_decrypt(item.get("password", ""))
                if addr and pwd:
                    out.append({"address": addr, "password": pwd})
            except Exception:
                continue
        return out

    # ------------------ SMTP sending ------------------

    @staticmethod
    def _smtp_for_address(address: str) -> Optional[Tuple[str, int, bool]]:
        """
        Returns (server, port, use_ssl). We default to TLS:587 unless Yahoo which prefers SSL:465.
        """
        domain = (address or "").split("@")[-1].lower()
        if "gmail.com" in domain:
            return ("smtp.gmail.com", 587, False)  # STARTTLS
        if "outlook.com" in domain or "hotmail.com" in domain or "live.com" in domain or "office365.com" in domain:
            return ("smtp.office365.com", 587, False)
        if "yahoo.com" in domain or "ymail.com" in domain:
            return ("smtp.mail.yahoo.com", 465, True)  # SSL
        return None

    def send_email(self, from_email: Dict[str, str], to_email: str, subject: str, body: str) -> str:
        """
        Send an email via SMTP. from_email must include plaintext {"address","password"}.
        """
        try:
            server_info = self._smtp_for_address(from_email.get("address", ""))
            if not server_info:
                return "Unsupported or unknown email provider."
            host, port, use_ssl = server_info

            message = MIMEMultipart()
            message["From"] = from_email["address"]
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain", "utf-8"))

            if use_ssl:
                with smtplib.SMTP_SSL(host, port) as server:
                    server.login(from_email["address"], from_email["password"])
                    server.send_message(message)
            else:
                with smtplib.SMTP(host, port) as server:
                    server.starttls()
                    server.login(from_email["address"], from_email["password"])
                    server.send_message(message)

            return "Email sent successfully."
        except Exception as e:
            return f"Error sending email: {e}"

    # ------------------ Gmail API (optional) ------------------

    def _ensure_gmail(self):
        if self._gmail is not None:
            return self._gmail
        if not (Credentials and InstalledAppFlow and build):
            return None
        try:
            creds = None
            if os.path.exists(self.gmail_token_path):
                creds = Credentials.from_authorized_user_file(self.gmail_token_path, GMAIL_SCOPES)
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(self.gmail_creds_path, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
                os.makedirs(os.path.dirname(self.gmail_token_path), exist_ok=True)
                with open(self.gmail_token_path, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())
            self._gmail = build("gmail", "v1", credentials=creds)
            return self._gmail
        except Exception:
            return None

    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Returns a small list of unread email summaries via Gmail API if available;
        returns [] otherwise (no crash).
        """
        svc = self._ensure_gmail()
        if not svc:
            return []

        try:
            res = svc.users().messages().list(
                userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results
            ).execute()
            messages = res.get("messages", [])
            out: List[Dict[str, str]] = []
            for m in messages:
                msg = svc.users().messages().get(userId="me", id=m["id"]).execute()
                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                out.append({
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "snippet": msg.get("snippet", ""),
                })
            return out
        except Exception:
            return []
