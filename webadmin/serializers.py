from rest_framework import serializers
from .models import Homepage, AboutPage, ContactPage, PrivacyPolicyPage, NewsletterPage, CustomPage, CompanyLogo, Category, FAQ, CardSection, CEO
from core.serializers import MentorSerializer, ReviewSerializer
from .models import MentoringCTA
from .models import MenttalkCTA
from .models import Footer, FooterLink, SocialLinks, CoreValue, BoardOfAdvisor, Teammates, BlogCard, CTACard, CTAButton



class SocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLinks
        fields = ['linkedin', 'instagram', 'facebook', 'youtube']

class FooterLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterLink
        fields = ['name', 'url', 'section']

class FooterSerializer(serializers.ModelSerializer):
    social_links = SocialLinksSerializer()
    links = FooterLinkSerializer(many=True)

    class Meta:
        model = Footer
        fields = ['company_name', 'about_text', 'hashtag', 'email', 'copyright', 'social_links', 'links']

class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLogo
        fields = ['name', 'logo', 'url']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'url']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']

class CardSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardSection
        fields = ['title', 'description', 'image']

class CEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CEO
        fields = ['name', 'image', 'position', 'company', 'quote']

class HomepageSerializer(serializers.ModelSerializer):
    top_mentors = MentorSerializer(many=True)
    company_logos = CompanyLogoSerializer(many=True)
    categories = CategorySerializer(many=True)
    reviews = ReviewSerializer(many=True)
    faqs = FAQSerializer(many=True)
    cards = CardSectionSerializer(many=True)
    ceo_details = CEOSerializer()

    class Meta:
        model = Homepage
        fields = ['mentor_search_placeholder', 'top_mentors', 'company_logos', 'categories', 'reviews', 'faqs', 'ceo_details', 'section_title', 'cards']

class CoreValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreValue
        fields = ['heading', 'description']

class BoardOfAdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardOfAdvisor
        fields = ['name', 'photo', 'bio']

class TeammatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teammates
        fields = ['name', 'photo', 'bio', 'linkedinurl', 'position']

class BlogCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCard
        fields = ['title', 'image', 'url']

class CTAButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTAButton
        fields = ['text', 'url']

class CTACardSerializer(serializers.ModelSerializer):
    buttons = CTAButtonSerializer(many=True, read_only=True)

    class Meta:
        model = CTACard
        fields = ['title', 'description', 'buttons']

class AboutPageSerializer(serializers.ModelSerializer):
    core_values = CoreValueSerializer(many=True, read_only=True)
    board_of_advisors = BoardOfAdvisorSerializer(many=True, read_only=True)
    teammates = TeammatesSerializer(many=True, read_only=True)
    blogs = BlogCardSerializer(many=True, read_only=True)
    cta_card = CTACardSerializer(read_only=True)

    class Meta:
        model = AboutPage
        fields = [
            'title', 'description', 'intro_image', 'sub_intro_image1', 'sub_intro_image2',
            'about_us_story', 'team_intro_text', 'teammates','core_values', 'board_of_advisors',
            'cta_card', 'blogs'
        ]

class ContactPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPage
        fields = '__all__'

class PrivacyPolicyPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicyPage
        fields = '__all__'

class NewsletterPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterPage
        fields = '__all__'

class CustomPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPage
        fields = '__all__'

class MentoringCTASerializer(serializers.ModelSerializer):
    class Meta:
        model = MentoringCTA
        fields = ['title', 'subtitle', 'description', 'video_url', 'top_mentors_count', 'happy_mentees_count', 'sessions_done_count', 'rating_stars', 'rating_label']


class MenttalkCTASerializer(serializers.ModelSerializer):
    class Meta:
        model = MenttalkCTA
        fields = ['title', 'subtitle', 'image', 'button_text', 'button_url', 'price', 'preorder_info', 'availability_info', 'extra_info']