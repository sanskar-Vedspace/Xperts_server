from django.urls import path
from .views import MentorAvailableSlotsView, TimeSlotListView, AvailabilityListView

urlpatterns = [
    path('availabilities/', AvailabilityListView.as_view(), name='availabilities'),
    path('time-slots/', TimeSlotListView.as_view(), name='time-slots'),
    path('mentor/<int:mentor_id>/available-slots/', MentorAvailableSlotsView.as_view(), name='mentor-available-slots'),
]
