from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests

# Create your views here.
@api_view(['GET'])
def book_list(request):
    url = "https://gutendex.com/books/?languages=fr"
    response = requests.get(url)
    return Response(response.json())

