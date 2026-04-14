import base64
import logging
import os.path
from datetime import datetime
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)

AIRBNB_SENDER_QUERY = "from:@airbnb.com"


class GmailService:

    def __init__(self, token_path: str = 'token.json', scopes: list[str] = ['https://www.googleapis.com/auth/gmail.readonly']):
        self.creds = None
        self.token_path = token_path
        self._scopes = scopes

        self._get_credentials()
        self.service = self._build_service()

    def _get_credentials(self) -> Credentials:
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self._scopes)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self._scopes
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

    def _build_service(self):
        try:
            service = build("gmail", "v1", credentials=self.creds)
            return service
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    def _get_email_body(self, payload: dict) -> str:
        """Recursively extract plain text body from an email payload."""
        mime_type = payload.get("mimeType", "")
        if mime_type == "text/plain":
            data = payload.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif mime_type.startswith("multipart/"):
            for part in payload.get("parts", []):
                body = self._get_email_body(part)
                if body:
                    return body
        return ""

    def fetch_airbnb_emails(self, max_results: int = 50) -> list[dict]:
        """Fetch emails from @airbnb.com. Returns list of dicts with subject, body, and date."""
        try:
            results = self.service.users().messages().list(
                userId="me",
                q=AIRBNB_SENDER_QUERY,
                maxResults=max_results,
            ).execute()
            message_refs = results.get("messages", [])
            if not message_refs:
                logger.info("No Airbnb emails found.")
                return []

            emails = []
            for ref in message_refs:
                msg = self.service.users().messages().get(
                    userId="me",
                    id=ref["id"],
                    format="full",
                ).execute()

                headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
                subject = headers.get("Subject", "")
                date_str = headers.get("Date", "")
                try:
                    date = parsedate_to_datetime(date_str)
                except Exception:
                    date = datetime.now()

                body = self._get_email_body(msg["payload"])
                emails.append({"subject": subject, "body": body, "date": date})
                logger.debug("Fetched Airbnb email: subject=%r, date=%s", subject, date)

            logger.info("Fetched %d Airbnb emails.", len(emails))
            return emails

        except HttpError as error:
            logger.error("Failed to fetch Airbnb emails: %s", error)
            return []

    def process_airbnb_emails(self, agent) -> list:
        """Fetch Airbnb emails and process each one through the concierge agent."""
        emails = self.fetch_airbnb_emails()
        messages = []
        for email in emails:
            message = agent.process_email(
                subject=email["subject"],
                body=email["body"],
                date=email["date"],
            )
            if message is not None:
                messages.append(message)
        return messages
