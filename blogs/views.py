# blogs/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import BlogPost, BlogCategory
from .serializers import BlogPostSerializer, BlogCategorySerializer

class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.request.query_params.get('category')
        if category_slug:
            return BlogPost.objects.filter(category__slug=category_slug)
        return super().get_queryset()

class BlogPostDetailView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view
    lookup_field = 'slug'  # Use the slug field for lookups

class BlogCategoryListView(generics.ListAPIView):  # New view for listing categories
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
