from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import random

from .models import Tweet
from .forms import TweetForm

# Create your views here.
def home_view(request, *args, **kwargs):
  return render(request, "pages/home.html", context={}, status=200)

def tweet_create_view(request, *args, **kewargs):
  form = TweetForm(request.POST or None)
  if form.is_valid():
    obj = form.save(commit=False)
    obj.save()
    form = TweetForm
  return render(request, "components/form.html",context={"form": form})

def tweet_list_view(request, *args, **kwargs):
  qs = Tweet.objects.all()
  tweet_list = [{"id": x.id, "content": x.content, "likes": random.randint(0, 123)} for x in qs]
  data = {
    "isUser": False,
    "response": tweet_list
  }
  return JsonResponse(data)

def tweet_detail_view(request, tweet_id, *args, **kwargs):
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
