from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Tweet

# Create your views here.
def home_view(request, *args, **kwargs):
  return HttpResponse("<h1>Yo World!!</h1>")

def home_detail_view(request, tweet_id, *args, **kwargs):
  data = {
    "id": tweet_id,
  }
  status = 200
  try:
    obj = Tweet.objects.get(id=tweet_id)
    data['content'] = obj.content
  except:
    # raise Http404
    data['message'] = "Not found"
    status = 404
  # return HttpResponse(f"<h1>Hiya {tweet_id} - {obj.content}</h1>")
  return JsonResponse(data, status=status)
