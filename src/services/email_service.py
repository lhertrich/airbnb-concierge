import logging
from imap_tools import MailBox, AND, MailMessage

from src.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, AIRBNB_SENDER
from src.agent.concierge import process_email

logger = logging.getLogger(__name__)

IMAP_HOST = "imap.gmail.com"


def poll_emails() -> None:
    logger.info("Polling for unread Airbnb emails...")
    try:
        with MailBox(IMAP_HOST).login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD) as mb:
            emails = list(mb.fetch(AND(from_=AIRBNB_SENDER, seen=False)))
            logger.info("Found %d unread Airbnb email(s).", len(emails))
            for msg in emails:
                _handle_email(msg)
    except Exception:
        logger.exception("Failed to poll emails.")


def _handle_email(msg: MailMessage) -> None:
    logger.info("Processing email: %r dated %s", msg.subject, msg.date)
    body = msg.text or msg.html or ""
    process_email(subject=msg.subject, body=body, date=msg.date)
