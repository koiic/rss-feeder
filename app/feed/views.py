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
from feed.utils import scrape_feed, ping_for_feed, update_new_feed

pagination = CustomPagination()


class FeedViewsets(viewsets.ModelViewSet):
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
        """
        override default create on viewset
        register a new feed and scrape the feed items
        Args:
            request ():  reuest object
            *args (): any
            **kwargs (): any

        Returns:
            Response (): a http response object
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # scrape feed info
        try:
            feed_, items = scrape_feed(request.data['link'])  # scrape the feed and items
            feed_['registered_by'] = request.user
            feed_['name'] = request.data['name']
            feed_['link'] = request.data['link']
            feed = serializer.create(validated_data=feed_)  # save the feed object

            item_serializer = ItemSerializer(data=items, many=True)
            item_serializer.is_valid(raise_exception=True)
            self.add_bulk_items(item_serializer.validated_data, feed)  # bulk create the items
            return Response({'success': True, 'message': messages['OK'].format('Feed')},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated], serializer_class=None)
    def ping(self, request, pk=None):
        """
        An endpoint to update feeds: persist the feed items if there are new updates on the rss feed
        Args:
            request (): request object
            pk (): The feed primary key

        Returns:
            Response (): an http response object
        """
        feed = self.get_object()
        return self.get_feed_items_update(feed)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated], url_path="me")
    def get_logged_user_feeds(self, request, pk=None):
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
        """
        fetch items for a single feed using the feed Id
        Args:
            request (): request object
            pk (): feed unique Id

        Returns:
            PaginatedResponse (): a paginated response of the items
        """
        feed = self.get_object()
        queryset = Item.objects.filter(feed=feed)
        read_param = request.GET.get('read', None)  # check if there is query params
        if read_param is not None:
            read_items = Read.objects.values_list("item__id")  # get item id of all read items
            if read_param.lower() == "true":
                queryset = queryset.filter(id__in=read_items)  # filter items by the already read items id
            elif read_param.lower() == "false":
                queryset = queryset.filter(~Q(id__in=read_items))  # filter items by the unread items id
        paginated_data = pagination.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_data, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=False, serializer_class=ItemSerializer, permission_classes=[IsAuthenticated],
            url_path='items')
    def fetch_all_items(self, request):
        """
                fetch all  items
                Args:
                    request (): request object
                Returns:
                    PaginatedResponse (): a paginated response of the items
                """
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
        """
        Fetch a single item using the item ID
        mark item as read
        Args:
            request (): Request  Object
            item_id (): the item UUID to update

        Returns:
            Response(): the httpResponse object
        """
        item = Item.objects.filter(pk=item_id).first()
        if item is None:
            return Response({'success': False, 'errors': messages['NOT_FOUND'].format('Item')},
                            status=status.HTTP_404_NOT_FOUND)
        # mark item as read
        if Read.objects.filter(item=item, user=request.user).exists():
            Read.objects.update(count=F('count') + 1)  # update the read count of an existing read items for a user
        else:
            Read.objects.create(item=item, user=request.user, count=1)
        # return item
        serializer = self.get_serializer(item)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=FollowerSerializer,
            permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        """
        GET endpoint to get the list of followers for a single feed
        Args:
            request (): request object
            pk (): unique feed id

        Returns:
            Response(): a http response object
        """
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
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=True, serializer_class=FollowerSerializer,
            permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """
           POST endpoint to follow a single feed
           Args:
               request (): request object
               pk (): unique feed id

           Returns:
               Response(): a http response object
        """
        feed = self.get_object()
        try:
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
        """
          POST endpoint to unfollow a single feed
          Args:
              request (): request object
              pk (): unique feed id

          Returns:
              Response(): a http response object
        """
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
        """
        method to bulk create items
        Args:
            payload (): Items list
            feed (): the feed instance that own to the items

        Returns:
            list of item instances
        """
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

    @staticmethod
    def get_feed_items_update(feed):
        """
        method to fetch updates for a feed
        Args:
            feed (): the feed object to fetch updates

        Returns:
            Response(): http response object
        """
        try:
            feed_, items, updated = ping_for_feed(feed)
            if updated:
                update_new_feed(feed, feed_, items)
                return Response({'success': True, 'message': messages['UPDATED'].format('Feed')},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'message': messages['NO_DATA_FOUND']},
                                status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response({'success': False, 'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
