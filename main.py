import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.services.email_service import poll_emails

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

CET = ZoneInfo("Europe/Berlin")


def main() -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(poll_emails, CronTrigger(hour=9, minute=0, timezone=CET))
    scheduler.add_job(poll_emails, CronTrigger(hour=17, minute=0, timezone=CET))
    logger.info("Scheduler started — polling at 09:00 and 17:00 CET.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
