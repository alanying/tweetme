from rest_framework import serializers
from .models import Tweet
from django.conf import settings

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTIONS = settings.TWEET_ACTIONS

class TweetActionSerializer(serializers.Serializer):
  id = serializers.IntegerField()
  action =  serializers.CharField()
  
  def validation_action(self, value):
    value = value.lower().strip()
    if not value in TWEET_ACTIONS:
      raise serializers.ValidationError("Invalid action.")
    return value
  
class TweetSerializer(serializers.ModelSerializer):
  likes = serializers.SerializerMethodField(read_only=True)
  class Meta:
    model = Tweet
    fields = ['id', 'content', 'likes']
  def get_likes(self, obj):
    return obj.likes.count()
  def validate_content(self, value):
    if len(value) > MAX_TWEET_LENGTH:
      raise serializers.ValidationError("Please shorten the tweet.")
    return value