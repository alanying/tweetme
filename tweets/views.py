import random

from django.http.response import Http404
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.http import is_safe_url
from django.conf import settings

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer, TweetActionSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Create your views here.
def home_view(request, *args, **kwargs):
  print(request.user or None)
  return render(request, "pages/home.html", context={}, status=200)

@api_view(['POST'])
# @authentication_classes([SessionAuthentication])    # don't need it if it's already been defined in settings
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
  serializer = TweetSerializer(data=request.POST)
  if serializer.is_valid(raise_exception=True):
    serializer.save(user=request.user)
    return Response(serializer.data, status=201)
  return Response({}, status=400)

@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
  qs = Tweet.objects.filter(id=tweet_id)
  if not qs.exists():
    return Response({}, status=404)
  obj = qs.first()
  serializer = TweetSerializer(obj)
  return Response(serializer.data, status=200)
  
@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
  qs = Tweet.objects.filter(id=tweet_id)
  if not qs.exist():
    return Response({}, status=404)
  qs = qs.filter(user=request.user)
  if not qs.exist():
    return Response({"message": "Only the author can delete."}, status=401)
  obj = qs.first()
  obj.delete()
  return Response({"message": "Tweet removed"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, tweet_id, *args, **kwargs):
  serializer = TweetActionSerializer(request.POST)
  if serializer.is_valid(raise_exception=True):
    data = serializer.validated_data
    tweet_id = data.get('id')
    action = data.get('action')
    
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exist():
      return Response({}, status=404)
    obj = qs.first()
    if action == "like":
      obj.likes.add(request.user)
    elif action == "unlike":
      obj.likes.delete(request.user)
    elif action == "retweet":
      # to do
      pass
  return Response({"message": "Tweet removed"}, status=200)

@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
  qs = Tweet.objects.all()
  serializer = TweetSerializer(qs, many=True)
  return Response(serializer.data, status=200)
  
  
def tweet_create_view_pure_django(request, *args, **kewargs):
  user = request.user
  if not request.user.is_authenticated:
    user = None
    if request.is_ajax():
      return JsonResponse({}, status=401)
    return redirect(settings.LOGIN_URL)
  form = TweetForm(request.POST or None)
  next_url = request.POST.get('next') or None
  if form.is_valid():
    obj = form.save(commit=False)
    obj.user = user
    obj.save()
    if request.is_ajax():
      return JsonResponse(obj.serialise(), status=201)
    if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
      return redirect(next_url)
    form = TweetForm
  if form.errors:
    if request.is_ajax():
      return JsonResponse(form.errors, status=400)
  return render(request, "components/form.html",context={"form": form})

def tweet_list_view_pure_django(request, *args, **kwargs):
  qs = Tweet.objects.all()
  # tweet_list = [{"id": x.id, "content": x.content, "likes": random.randint(0, 123)} for x in qs]
  tweet_list = [x.serialise() for x in qs]
  data = {
    "isUser": False,
    "response": tweet_list
  }
  return JsonResponse(data)

def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
  data = {
    "id": tweet_id,
  }
  status = 200
  try:
    obj = Tweet.objects.get(id=tweet_id)
    data['content'] = obj.content
  except:
    data['message'] = "Not found"
    status = 404
  return JsonResponse(data, status=status)
