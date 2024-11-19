from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Mentor, Expertise, Tool, Review, MentorTimeBlock
from workex.models import WorkExperience
from core.models import Availability,TimeSlot,Booking,CustomUser

from time_blocks.models import TimeBlock
from time_blocks.serializers import TimeBlockSerializer
from django.shortcuts import get_object_or_404 
User = get_user_model()

class AvailabilitySerializer(serializers.ModelSerializer):
    slots = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ['id','mentor', 'date', 'start_time', 'end_time', 'slots']

    def get_slots(self, obj):
        # Fetch the mentor from the availability object
        mentor = obj.mentor
        time_slots = mentor.mentor_time_slots.all()  # Fetch the mentor's active time slots

        slot_data = {}

        # Iterate over the mentor's time slots to calculate available slots
        for time_slot in time_slots:
            duration = time_slot.duration
            slots_for_duration = obj.get_available_slots(duration)
            slot_data[f'slots_{duration}_mins'] = slots_for_duration

        return slot_data

from django.shortcuts import get_object_or_404

class MenteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Assuming CustomUser is your user model
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'short_intro']

class BookingSerializer(serializers.ModelSerializer):
    mentor = serializers.StringRelatedField(read_only=True)
    mentee = MenteeSerializer(read_only=True)  # Assuming you have a MenteeSerializer
    availability = serializers.StringRelatedField(read_only=True)
    time_slot = serializers.StringRelatedField(read_only=True)
    booking_status = serializers.CharField(read_only=True)  # Read-only for mentees
    meeting_link = serializers.CharField(read_only=True)  
    class Meta:
        model = Booking
        fields = ['id', 'mentee', 'mentor', 'availability', 'time_slot', 'start_time', 'end_time', 'payment_status', 'wallet_payment_status','booking_status', 'created_at','meeting_link']
        read_only_fields = ['mentee', 'mentor', 'payment_status','wallet_payment_status', 'created_at', 'booking_status']

    def create(self, validated_data):
        # Automatically assign the logged-in user as the mentee
        mentee = self.context['request'].user

        # Extract availability and time_slot IDs from the incoming request
        availability_id = self.context['request'].data.get('availability_id')
        time_slot_id = self.context['request'].data.get('time_slot_id')

        # Fetch the actual Availability and TimeSlot objects based on the IDs
        availability = get_object_or_404(Availability, id=availability_id)
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        # Add mentor, availability, and time_slot to the validated data
        validated_data['mentee'] = mentee
        validated_data['mentor'] = availability.mentor
        validated_data['availability'] = availability
        validated_data['time_slot'] = time_slot

        # Check if this time slot is available for booking
        overlapping_bookings = Booking.objects.filter(
            mentor=availability.mentor,
            availability=availability,
            start_time__lt=validated_data['end_time'],
            end_time__gt=validated_data['start_time']
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError("The selected time slot is already booked.")

        # Create the booking
        booking = Booking.objects.create(**validated_data)
        return booking



class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'duration', 'price']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'mentee')
        user = User.objects.create_user(**validated_data, user_type=user_type)
        Token.objects.create(user=user)
        return user

class ConvertToMentorSerializer(serializers.Serializer):
    username = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = ['name','expertise_description']

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['name']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source='reviewer.username')
    reviewer_profile_picture = serializers.ImageField(source='reviewer.profile_picture', read_only=True)

    class Meta:
        model = Review
        fields = ['mentor','reviewer','reviewer_profile_picture', 'content', 'rating', 'created_at']

class WorkExperienceSerializer(serializers.ModelSerializer):
    industry_expertise = ExpertiseSerializer(many=True)
    
    class Meta:
        model = WorkExperience
        fields = ['id', 'company_name', 'work_description', 'date_started', 'date_ended', 'currently_working', 'industry_expertise']
        extra_kwargs = {
            'date_started': {'format': '%Y-%m-%d'},
            'date_ended': {'format': '%Y-%m-%d'}
        }

    def validate(self, data):
        if data.get('currently_working') and data.get('date_ended'):
            raise serializers.ValidationError("Currently working experience should not have an end date.")
        return data

class MentorTimeBlockSerializer(serializers.ModelSerializer):
    time_block = TimeBlockSerializer()

    class Meta:
        model = MentorTimeBlock
        fields = ['time_block', 'price']

class MentorSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='username.username')
    mentor_time_blocks = MentorTimeBlockSerializer(many=True)
    expertise = ExpertiseSerializer(many=True)
    toolkits_used = ToolSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    work_experiences = WorkExperienceSerializer(many=True)
    all_expertise = ExpertiseSerializer(many=True, read_only=True, source='expertise_model.all')
    all_tools = ToolSerializer(many=True, read_only=True, source='tool_model.all')
    availabilities = AvailabilitySerializer(many=True, source='mentor_availabilities')
    time_slots = TimeSlotSerializer(many=True, source='mentor_time_slots')
    id = serializers.ReadOnlyField(source='username.id')
    joined_date = serializers.DateField(read_only=True)
    next_availability = serializers.ReadOnlyField()
    class Meta:
        model = Mentor
        fields = [
            'id','username', 'name', 'description', 'short_intro', 'introductory_video',
            'expertise', 'toolkits_used', 'reviews', 'linkedin','location',
            'mentor_time_blocks', 'work_experiences', 'availabilities','time_slots',
            'all_expertise', 'all_tools', 'profile_picture','joined_date', 'next_availability'
        ]


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.short_intro = validated_data.get('short_intro', instance.short_intro)
        instance.introductory_video = validated_data.get('introductory_video', instance.introductory_video)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)

        if 'expertise' in validated_data:
            expertise_data = validated_data.pop('expertise')
            instance.expertise.set([Expertise.objects.get(name=exp['name']) for exp in expertise_data])

        if 'toolkits_used' in validated_data:
            toolkits_data = validated_data.pop('toolkits_used')
            instance.toolkits_used.set([Tool.objects.get(name=tool['name']) for tool in toolkits_data])

        if 'work_experiences' in validated_data:
            work_experiences_data = validated_data.pop('work_experiences')
            existing_experience_ids = [exp['id'] for exp in work_experiences_data if 'id' in exp]
            WorkExperience.objects.filter(mentor=instance).exclude(id__in=existing_experience_ids).delete()
            for exp_data in work_experiences_data:
                exp_id = exp_data.get('id', None)
                if exp_id:
                    work_experience = WorkExperience.objects.get(id=exp_id, mentor=instance)
                    work_experience.company_name = exp_data.get('company_name', work_experience.company_name)
                    work_experience.work_description = exp_data.get('work_description', work_experience.work_description)
                    work_experience.date_started = exp_data.get('date_started', work_experience.date_started)
                    work_experience.date_ended = exp_data.get('date_ended', work_experience.date_ended)
                    work_experience.currently_working = exp_data.get('currently_working', work_experience.currently_working)
                    work_experience.industry_expertise.set([Expertise.objects.get(name=exp['name']) for exp in exp_data.get('industry_expertise', [])])
                    work_experience.save()
                else:
                    new_exp = WorkExperience.objects.create(
                        mentor=instance,
                        company_name=exp_data['company_name'],
                        work_description=exp_data['work_description'],
                        date_started=exp_data['date_started'],
                        date_ended=exp_data.get('date_ended', None),
                        currently_working=exp_data.get('currently_working', False),
                    )
                    new_exp.industry_expertise.set([Expertise.objects.get(name=exp['name']) for exp in exp_data.get('industry_expertise', [])])
                    new_exp.save()

        if 'mentor_time_blocks' in validated_data:
            mentor_time_blocks_data = validated_data.pop('mentor_time_blocks')
            instance.mentor_time_blocks.all().delete()  # Clear existing time blocks
            for mtb_data in mentor_time_blocks_data:
                time_block_id = mtb_data.get('time_block')
                time_block = get_object_or_404(TimeBlock, id=time_block_id)
                MentorTimeBlock.objects.create(
                    mentor=instance,
                    time_block=time_block,  # This now correctly resolves the TimeBlock instance
                    price=mtb_data['price']
                )

        instance.save()
        return instance
class SuggestedMentorSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='username.username')
    expertise = ExpertiseSerializer(many=True, source='mentor-expertise')
    profile_picture = serializers.ImageField(source='mentor-profile_picture', read_only=True)

    class Meta:
        model = Mentor
        fields = [ 'username', 'expertise', 'profile_picture']  


from rest_framework import serializers
from .models import Booking

class MenteeBookingSerializer(serializers.ModelSerializer):
    booking_date = serializers.SerializerMethodField()
    booking_start_time = serializers.SerializerMethodField()
    booking_end_time = serializers.SerializerMethodField()
    mentor_name = serializers.SerializerMethodField()
    mentor_profile_picture = serializers.SerializerMethodField()
    meeting_link = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'mentor_name',
            'mentor_profile_picture',
            'availability',
            'time_slot',
            'booking_date',
            'booking_start_time',
            'booking_end_time',
            'payment_status',
            'meeting_link',
            'created_at',
        ]

    def get_booking_date(self, obj):
        return obj.start_time.date() if obj.start_time else None

    def get_booking_start_time(self, obj):
        return obj.start_time.isoformat() if obj.start_time else None

    def get_booking_end_time(self, obj):
        return obj.end_time.isoformat() if obj.end_time else None

    def get_mentor_name(self, obj):
        return obj.mentor.name if obj.mentor else None

    def get_mentor_profile_picture(self, obj):
        if obj.mentor and obj.mentor.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.mentor.profile_picture.url) if request else obj.mentor.profile_picture.url
        return None


class MenteeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'address', 'interests',
            'city', 'state', 'pin', 'country', 'profile_picture', 'short_intro', 'company_name', 
            'designation', 'gst_number', 'age_of_startup', 'industry_of_startup'
        ]
        extra_kwargs = {
            'username': {'read_only': True},  # Read-only field
            'email': {'read_only': True},  # Read-only field
            'profile_picture': {'required': False, 'allow_null': True},  # Allow null for profile picture
        }

    def update(self, instance, validated_data):
        # Pop and handle the profile picture separately
        profile_picture = validated_data.pop('profile_picture', None)
        
        # Pop the interests if provided
        interests = validated_data.pop('interests', None)

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle profile picture upload
        if profile_picture:
            instance.profile_picture = profile_picture

        # Handle Many-to-Many Field (Interests)
        if interests is not None:
            instance.interests.set(interests)  # Update interests relationship

        instance.save()
        return instance

class AvailableInterestsSerializer(serializers.ModelSerializer):
    mentee_interests = serializers.SerializerMethodField()

    class Meta:
        model = Expertise
        fields = ['id', 'name', 'mentee_interests']

    def get_mentee_interests(self, obj):
        mentee = self.context.get('mentee')
        return mentee.interests.filter(id=obj.id).exists()


    
class MentorBookingSerializer(serializers.ModelSerializer):
    mentee_id = serializers.CharField(source='mentee.id')
    mentee_first_name = serializers.CharField(source='mentee.first_name')
    mentee_last_name = serializers.CharField(source='mentee.last_name')
    mentee_profile_picture = serializers.SerializerMethodField()
    booking_date = serializers.SerializerMethodField()
    booking_start_time = serializers.SerializerMethodField()
    booking_end_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'mentee_id', 
            'mentee_first_name', 
            'mentee_last_name', 
            'mentee_profile_picture', 
            'booking_date', 
            'booking_start_time', 
            'booking_end_time', 
            'payment_status',
            'meeting_link',
        ]

    def get_mentee_profile_picture(self, obj):
        # Return the mentee's profile picture URL if available
        if obj.mentee.profile_picture:
            return self.context['request'].build_absolute_uri(obj.mentee.profile_picture.url)
        return None

    def get_booking_date(self, obj):
        return obj.start_time.date()

    def get_booking_start_time(self, obj):
        return obj.start_time.time()

    def get_booking_end_time(self, obj):
        return obj.end_time.time()
