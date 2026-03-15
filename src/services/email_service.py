import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)


class GmailService:

    def __init__(self, token_path: str='token.json', scopes: list[str]=['https://www.googleapis.com/auth/gmail.readonly']):
        self.creds = None
        self.token_path = token_path
        self._scopes = scopes

        self._get_credentials()
        self.service = self._build_service()


    def _get_credentials(self) -> Credentials:
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self._scopes)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", self._scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    
    def _build_service(self):
        try:
            service = build("gmail", "v1", credentials=self.creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    
    def query_email(self):
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                logger.info("No labels found.")
            
            return labels

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None
