import uuid

from django.db import models

# Create your models here.
from core import settings


class Base(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Feed(Base):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    link = models.URLField()
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                      related_name="feed_owners")
    last_build_date = models.DateTimeField()
    ttl = models.IntegerField(null=True)
    name = models.CharField(max_length=50, unique=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('name', 'registered_by')

    def __str__(self):
        return f'{self.title}'


class Item(Base):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    link = models.URLField()
    author = models.CharField(max_length=25, null=True, blank=True)
    guid = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    comments_url = models.URLField(null=True, blank=True)
    published_at = models.DateTimeField()
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="feed_items")

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.feed.name} - {self.title}'


class Followers(Base):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_followings")
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="feed_followers")

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.feed.title} - {self.user.firstname}'


class Read(Base):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                             related_name="user_reads")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_reads")
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.item.title} - {self.user.firstname}'


class Activity(Base):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                             related_name="user_activities")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_activities")
    is_read = models.BooleanField()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.item.title} - {self.user.firstname}'
