from rest_framework import serializers
from .models import WorkExperience
from industry.models import Expertise

class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = ['name']

class WorkExperienceSerializer(serializers.ModelSerializer):
    industry_expertise = ExpertiseSerializer(many=True)

    class Meta:
        model = WorkExperience
        fields = [
            'id', 'company_name', 'work_description', 'date_started', 
            'date_ended', 'currently_working', 'industry_expertise'
        ]

    def create(self, validated_data):
        expertise_data = validated_data.pop('industry_expertise')
        work_experience = WorkExperience.objects.create(**validated_data)
        for expertise in expertise_data:
            work_experience.industry_expertise.add(Expertise.objects.get(name=expertise['name']))
        return work_experience
