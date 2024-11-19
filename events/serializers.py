from rest_framework import serializers
from .models import Event, EventRegistration, EventPayment

class EventRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    mentor_name = serializers.CharField(source='event.mentor.username', read_only=True)
    slug = serializers.CharField(source='event.slug', read_only=True)
    photo = serializers.ImageField(source='event.photo', read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'user', 'event', 'event_title','photo', 'slug', 'mentor_name', 'registration_date', 'payment_status']

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data.get('event')

        if EventRegistration.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError('You have already registered for this event.')

        registration = EventRegistration(user=user, event=event, payment_status='Pending')
        registration.save()
        return registration

from rest_framework import serializers
from .models import Event, EventRegistration, EventPayment

class EventSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)  # Include mentor's username

    class Meta:
        model = Event
        fields = '__all__'

    def get_participants(self, obj):
        registrations = EventRegistration.objects.filter(event=obj)
        return [registration.user.username for registration in registrations]



class EventPaymentSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event_registration.event.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventPayment
        fields = ['id', 'user', 'user_name', 'event_registration', 'event_title', 'amount', 'payment_date', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'verified']
        read_only_fields = ['payment_date', 'verified']
