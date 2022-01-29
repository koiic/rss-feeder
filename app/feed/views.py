from django.db.models import F, Q
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sentry_sdk import capture_exception

from core.messages import messages
from core.pagination import CustomPagination
from feed.filters import FeedFilters, ItemFilters
from feed.models import Feed, Item, Followers, Activity, Read
from feed.serializers import FeedSerializer, ItemSerializer, FollowerSerializer
from feed.utils import scrape_feed

pagination = CustomPagination()


class FeedViewsets(viewsets.ModelViewSet):
    """Feed view sets"""
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    # filter_class = FeedFilters
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['title', 'slug']
    ordering_fields = ['updated_at']

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['list']:
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'partial_update']:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, pk=None):
        queryset = self.get_queryset().filter(registered_by=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data},
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=ItemSerializer, permission_classes=[IsAuthenticated])
    def items(self, request, pk=None):
        feed = self.get_object()
        queryset = Item.objects.filter(feed=feed)
        read_param = request.GET.get('read', None)
        if read_param is not None:
            read_items = Read.objects.values_list("item__id")
            if read_param.lower() == "true":
                queryset = queryset.filter(id__in=read_items)
            elif read_param.lower() == "false":
                queryset = queryset.filter(~Q(id__in=read_items))
        paginated_data = pagination.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_data, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=False, serializer_class=ItemSerializer, permission_classes=[IsAuthenticated],
            url_path='items')
    def fetch_all_items(self, request):
        queryset = Item.objects.filter()
        read_param = request.GET.get('read', None)
        if read_param is not None:
            read_items = Read.objects.values_list("item__id")
            if read_param.lower() == "true":
                queryset = queryset.filter(id__in=read_items)
            elif read_param.lower() == "false":
                queryset = queryset.filter(~Q(id__in=read_items))
        paginated_data = pagination.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_data, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=False, serializer_class=ItemSerializer,
            url_path='items/(?P<item_id>[^/.]+)')
    def item(self, request, item_id):
        item = Item.objects.filter(pk=item_id).first()
        if item is None:
            return Response({'success': False, 'errors': messages['NOT_FOUND'].format('Item')},
                            status=status.HTTP_404_NOT_FOUND)
        # mark item as read
        if Read.objects.filter(item=item, user=request.user).exists():
            Read.objects.update_or_create(item=item, user=request.user, defaults={'count': F('count') + 1})
        else:
            Read.objects.create(item=item, user=request.user, count=1)
        # return item
        serializer = self.get_serializer(item)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['GET', 'POST'], detail=True, serializer_class=FollowerSerializer,
            permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        feed = self.get_object()
        try:
            if self.request.method == 'GET':
                followers = Followers.objects.filter(feed=feed)
                serializer = self.get_serializer(followers, many=True)
                data = {
                    'count': followers.count(),
                    'followers': serializer.data
                }
                return Response({'success': True, 'data': data})
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

    @action(methods=['POST'], detail=True, serializer_class=None,
            permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        feed = self.get_object()
        try:
            obj = Followers.objects.filter(user=request.user, feed=feed).first()
            if obj is None:
                return Response({'success': False, 'errors': messages['NOT_FOUND'].format('Feed')},
                                status=status.HTTP_404_NOT_FOUND)
            obj.delete()
            return Response({'success': True, 'message': messages['UNFOLLOWED']},
                            status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
