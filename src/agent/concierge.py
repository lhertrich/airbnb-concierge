import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def process_email(subject: str, body: str, date: datetime) -> None:
    """Parse and act on a raw Airbnb email. Agent logic to be added."""
    # TODO: implement agent-based email parsing
    logger.info("Agent received email — subject: %r, date: %s", subject, date)
