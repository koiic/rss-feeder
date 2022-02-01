from uuid import UUID

from celery import shared_task
import logging

from celery.utils.serialization import raise_with_context
from django.template.loader import get_template

from core import settings
from feed.models import Feed, Item
from feed.utils import ping_for_feed, update_new_feed
from user.utils import send_email

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def scrape_new_feed_task(self):
    """
    A task to scrape feed items for all feeds in background asynchronously
    """
    for id_ in Feed.objects.values_list('pk'):
        scrape_single_user_field.apply_async(id_)


@shared_task(bind=True)
def scrape_single_user_field(self, feed_id):
    """

    Args:
        self (): The task instance
        feed_id (): single feed id

    Returns:
        void () : call the function to update all items for feeds

    """
    feed = Feed.objects.filter(pk=UUID(feed_id)).first()
    try:
        feed_, items, updated = ping_for_feed(feed)  # ping for updates
        if updated:
            logger.info(f"new update received for  -> {feed.name}")
            update_new_feed(feed, feed_, items)  # persist the new feed items to database
        else:
            logger.info(f"No new Updated for feed -> {feed.name}")
    except Exception as exc:
        last_try = self.request.retries >= self.max_retries - 1
        if last_try:
            logger.exception(f"failure email sent to user - {str(exc)}")
            # send notification to user
            send_fail_notification({
                "email": feed.registered_by.email,
                "fullname": feed.registered_by.firstname,
                "link": f"{settings.ALLOWED_HOSTS[0]}:8000/api/v1/feeds/{feed.id}/ping",
                "title": feed.title
            })
            raise_with_context(exc)
        else:
            logger.info(f"retrying cause of exception")
            self.retry(
                exc=exc, countdown=15, max_retries=2, retry_backoff=True, retry_backoff_max=10 * 60, retry_jitter=False
            )
        raise_with_context(exc)


def send_fail_notification(email_data):
    html_template = get_template('emails/failed_feeds_update.html')
    text_template = get_template('emails/failed_feeds_update.txt')
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email('Feed Update Failed',
               email_data['email'], html_alternative, text_alternative)
