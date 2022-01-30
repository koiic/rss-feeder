from rest_framework import serializers

from feed.models import Feed, Item, Followers, Read
from user.serializers import ListUserSerializer, UserFollowerSerializer


class FeedSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Feed
        fields = '__all__'
        extra_kwargs = {
            'registered_by': {'read_only': True},
            'title': {'read_only': True},
            'description': {'read_only': True},
            'ttl': {'read_only': True},
            'last_build_date': {'read_only': True},
        }

    def create(self, validated_data):
        # Pass data needed from Feed registration
        new_feed_instance = self.Meta.model(**validated_data)
        new_feed_instance.save()
        return new_feed_instance

    def get_follower_count(self, feed):
        return feed.feed_followers.count()  # get the read count


class ItemSerializer(serializers.ModelSerializer):
    read_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Item
        exclude = ('feed',)

    def get_read_count(self, item):
        return item.item_reads.count()  # get the read count


class FollowerSerializer(serializers.ModelSerializer):
    user = UserFollowerSerializer(read_only=True)

    class Meta:
        model = Followers
        exclude = ('feed',)


class RegisterFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ("link", "name")
