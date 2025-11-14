from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from django.urls import path
from . import views

BASE_URL = "https://gutendex.com/books"

# Create your views here.

# liste des livres (avec search & languages)
@api_view(['GET'])
def book_list(request):
    search = request.GET.get("search", "")
    language = request.GET.get("language", "")

    params = []

    if search:
        params.append(f"search={search}")
    if language:
        params.append(f"languages={language}")

    url = BASE_URL
    if params:
        url += "?" + "&".join(params)

    response = requests.get(url)
    return Response(response.json())

# liste des livres par language
@api_view(['GET'])
def book_langagage(request, language):
    url = f"{BASE_URL}?languages={language}"
    response = requests.get(url)
    return Response(response.json())

# détail d'un livre
@api_view(['GET'])
def book_detail(request, book_id):
    url = f"{BASE_URL}/{book_id}"
    response = requests.get(url)
    return Response(response.json())

# image de couverture d'un livre
@api_view(['GET'])
def cover_image(request, book_id):
    url = f"{BASE_URL}/{book_id}"
    response = requests.get(url)
    data = response.json()

    cover_url = data.get("formats", {}).get("image/jpeg", None)

    if not cover_url:
        return Response({"error": "No cover image available"}, status=404)

    return Response({"cover_image_url": cover_url})