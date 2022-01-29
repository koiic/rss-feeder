from celery import shared_task

from feed.models import Feed, Item
from feed.utils import ping_for_feed


@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def scrape_new_feed():
    feeds = Feed.objects.all()
    for feed in feeds:
        feed_, items, updated = ping_for_feed(feed)
        if updated:
            print(f"new update received for  -> {feed.name}")
            feed.last_build_date = feed_.get('last_build_date')
            feed.save(update_fields=['last_build_date'])
            for item in items:
                guid = item.pop('guid')
                Item.objects.get_or_create(guid=guid, feed=feed, defaults=item)
        else:
            print(f"No new Updated for feed -> {feed.name}")
