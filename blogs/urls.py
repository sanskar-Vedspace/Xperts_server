# blogs/urls.py

from django.urls import path
from .views import BlogPostListCreateView, BlogPostDetailView, BlogCategoryListView

urlpatterns = [
    path('blogs/', BlogPostListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<slug:slug>/', BlogPostDetailView.as_view(), name='blog-detail'),
    path('categories/', BlogCategoryListView.as_view(), name='category-list'),  # New endpoint for listing categories
]
