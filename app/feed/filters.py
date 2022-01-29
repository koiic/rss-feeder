
# filters.py
from datetime import timedelta

from django_filters import rest_framework as filters
from django.db.models import Q

from feed.models import Read, Item, Feed


class FeedFilters(filters.FilterSet):
    read = filters.BooleanFilter(label='read', method='filter_read')
    unread = filters.BooleanFilter(label='unread', method='filter_read')

    class Meta:
        model = Feed
        # 'filterset_fields' simply proxies the 'Meta.fields' option
        # Also, it isn't necessary to include declared fields here
        fields = []

    def filter_read(self, queryset, name, value):
        print(name, value)
        read_items = Read.objects.values_list("item__id")
        print(read_items, "===>><><>")
        print(queryset.filter(feed_items__in=read_items))
        return queryset.filter(feed_items__in=read_items)

    def filter_unread(self, queryset, name, value):
        print(name, value)
        unread_items = Read.objects.values_list("item__id")
        return queryset.filter(~Q(feed_items__in=unread_items))


class ItemFilters(filters.FilterSet):
    read = filters.BooleanFilter(label='read', method='filter_read')
    unread = filters.BooleanFilter(label='unread', method='filter_read')

    class Meta:
        model = Item
        # 'filterset_fields' simply proxies the 'Meta.fields' option
        # Also, it isn't necessary to include declared fields here
        fields = []

    def filter_read(self, queryset, name, value):
        print(name, value)
        read_items = Read.objects.values_list("item__id")
        print(queryset.filter(id__in=read_items))
        return queryset.filter(id__in=read_items)

    def filter_unread(self, queryset, name, value):
        print(name, value)
        unread_items = Read.objects.values_list("item__id")
        return queryset.filter(~Q(id__in=unread_items))