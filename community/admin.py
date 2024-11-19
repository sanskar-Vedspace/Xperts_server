from django.contrib import admin
from .models import SubscriptionPlan, Subscription, SubscriptionPayment, Group, Post, Like, Comment, Share, Follow

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price', 'quarterly_price', 'annual_price')  # Update to show individual prices

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'cycle', 'is_active', 'started_at', 'ends_at')

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'payment_date', 'razorpay_order_id', 'transaction_id')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'expertise')
    list_filter = ('expertise',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_type', 'expertise', 'created_at')
    list_filter = ('content_type', 'expertise', 'author')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')

@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
