from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
import logging

from django.template.loader import get_template

from feed.models import Feed, Item
from feed.utils import ping_for_feed, update_new_feed
from user.utils import send_email

logger = logging.getLogger(__name__)


@shared_task
def scrape_new_feed():
    """
    scrape new feeds item
    task is run in background asynchronously
    """
    current_feed = None
    try:
        feeds = Feed.objects.all()
        for feed in feeds:
            feed_, items, updated = ping_for_feed(feed)  # ping for updates
            if updated:
                current_feed = feed
                logger.info(f"new update received for  -> {feed.name}")
                update_new_feed(feed, feed_, items)  # persist the new feed items to database
            else:
                logger.info(f"No new Updated for feed -> {feed.name}")
    except Exception as e:
        logger.exception(e)
        try:
            logger.info(f"retrying cause of exception")
            scrape_new_feed.retry(
                exc=e, countdown=2 * 60, max_retries=4, retry_backoff=True, retry_backoff_max=10 * 60, retry_jitter=True
            )
        except MaxRetriesExceededError:
            # send notification to user
            send_fail_notification({
                "email": current_feed.registered_by.email,
                "fullname": current_feed.registered_by.firstname,
                "link": current_feed.link,
            })
            logger.exception(e)
            raise Exception(str(e))


def send_fail_notification(email_data):
    html_template = get_template('emails/failed_feeds_update.html')
    text_template = get_template('emails/failed_feeds_update.txt')
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email('Feed Update Failed',
               email_data['email'], html_alternative, text_alternative)
