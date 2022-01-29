from django.contrib import admin

# Register your models here.
from feed.models import Feed, Followers, Activity, Item

admin.site.register(Feed)
admin.site.register(Item)
admin.site.register(Followers)
admin.site.register(Activity)
