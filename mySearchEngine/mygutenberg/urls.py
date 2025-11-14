from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.book_list), # works 
    path("book/<int:book_id>/", views.book_detail), # works
    path("books/lang/<str:language>/", views.book_langagage), # doesn't work
    path("book/<int:book_id>/coverImage/", views.cover_image),
]