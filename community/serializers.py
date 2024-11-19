from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, SubscriptionPayment, Group, Post, Like, Comment, Share, Follow
from industry.serializers import ExpertiseSerializer
from core.models import CustomUser


class UserDetailSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name','profile_picture', 'short_intro']

    def get_profile_picture(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None
    
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'monthly_price', 'quarterly_price', 'annual_price']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'cycle', 'is_active', 'started_at', 'ends_at']

class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer()

    class Meta:
        model = SubscriptionPayment
        fields = ['id', 'subscription', 'amount', 'payment_date', 'transaction_id']

class GroupSerializer(serializers.ModelSerializer):
    expertise = ExpertiseSerializer()  # Serialize the related Expertise data
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'expertise', 'members', 'posts']

    def get_posts(self, obj):
        posts = obj.posts.all()
        return PostSerializer(posts, many=True).data
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user','post', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)  # Include user details

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    expertise = ExpertiseSerializer()  # Serialize the expertise field
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)  # Include comments in the post
    author_name = serializers.SerializerMethodField()  # Custom field for author's full name
    profile_picture = serializers.SerializerMethodField()  # Custom field for profile picture
    short_intro = serializers.SerializerMethodField()  # Custom field for short intro
    is_liked = serializers.SerializerMethodField()  # New field to indicate if the user has liked the post
    pdf = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_name', 'profile_picture', 'short_intro', 'content_type', 'content', 
            'image', 'document', 'pdf', 'poll_options', 'created_at', 'likes_count', 'comments_count', 
            'shares_count', 'comments', 'expertise', 'is_liked'  # Include is_liked in the serialized fields
        ]

    def get_author_name(self, obj):
        if obj.author.first_name or obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}".strip()
        return obj.author.username

    def get_profile_picture(self, obj):
        if hasattr(obj.author, 'mentor_profile') and obj.author.mentor_profile.profile_picture:
            return obj.author.mentor_profile.profile_picture.url
        return obj.author.profile_picture.url if obj.author.profile_picture else None

    def get_short_intro(self, obj):
        if hasattr(obj.author, 'mentor_profile'):
            return obj.author.mentor_profile.short_intro or "No intro available"
        return obj.author.short_intro or "No intro available"

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_shares_count(self, obj):
        return obj.shares.count()

    def get_is_liked(self, obj):
        # Check if the current user has liked this post
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_pdf(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'build_absolute_uri'):
            return request.build_absolute_uri(obj.pdf.url) if obj.pdf else None
        return None  # Return None if the request or PDF URL is unavailable


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'post', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
