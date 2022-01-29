from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sentry_sdk import capture_exception

from core.messages import messages
from core.pagination import CustomPagination
from feed.models import Feed, Item, Followers
from feed.serializers import FeedSerializer, ItemSerializer, FollowerSerializer
from feed.utils import scrape_feed

pagination = CustomPagination()


class FeedViewsets(viewsets.ModelViewSet):
    """Employee view sets"""
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['title', 'slug']
    ordering_fields = ['updated_at']

    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return RegisterFeedSerializer
    #     else:
    #         return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # scrape feed info
        try:
            feed_, items = scrape_feed(request.data['link'])
            feed_['registered_by'] = request.user
            feed_['name'] = request.data['name']
            feed = serializer.create(validated_data=feed_)
            # save items
            item_serializer = ItemSerializer(data=items, many=True)
            item_serializer.is_valid(raise_exception=True)
            self.add_bulk_items(item_serializer.validated_data, feed)
            return Response({'success': True, 'message': messages['OK'].format('Feed')},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=True, serializer_class=ItemSerializer, permission_classes=[IsAuthenticated])
    def items(self, request, pk=None):
        feed = self.get_object()
        objs = Item.objects.filter(feed=feed)
        paginated_data = pagination.paginate_queryset(objs, request)
        serializer = self.get_serializer(paginated_data, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['GET', 'POST'], detail=True, serializer_class=FollowerSerializer)
    def follow(self, request, pk=None):
        feed = self.get_object()
        try:
            if self.request.method == 'GET':
                followers = Followers.objects.filter(feed=feed)
                serializer = self.get_serializer(followers, many=True)
                return Response({'success': True, 'data': serializer.data})
            elif self.request.method == 'POST':
                obj, created = Followers.objects.get_or_create(user=request.user, feed=feed)
                if created:
                    return Response({'success': True, 'message': messages['FOLLOWED']},
                                    status=status.HTTP_200_OK)
                return Response({'success': True, 'message': messages['FOLLOWING']},
                                status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(methods=['GET', 'POST'], detail=True, serializer_class=FollowerSerializer)
    # def unfollow(self, request, pk=None):
    #     pass

    @staticmethod
    def add_bulk_items(payload, feed):
        item_list = []
        batch_size = 20
        for data in payload:
            item = Item(
                title=data.get('title'),
                description=data.get('description'),
                published_at=data.get('published_at'),
                link=data.get('link'),
                guid=data.get('guid'),
                comments_url=data.get('comments_url'),
                author=data.get('author'),
                category=data.get('category'),
                feed=feed
            )
            item_list.append(item)
        return Item.objects.bulk_create(item_list, batch_size)
