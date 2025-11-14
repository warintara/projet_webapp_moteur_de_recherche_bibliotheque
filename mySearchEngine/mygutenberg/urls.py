from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.book_list),
    path("book/<int:book_id>/", views.book_detail),
    path("books/lang/<str:langage>/", views.book_langagage),
    path("book/<int:book_id>/coverImage/", views.cover_image),
]