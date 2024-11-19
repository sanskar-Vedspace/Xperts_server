from django.db import models
from solo.models import SingletonModel
from core.models import Mentor, Review
from ckeditor_uploader.fields import RichTextUploadingField

class CompanyLogo(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/')
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='category_icons/')
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

class CardSection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='card_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class CEO(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ceo_images/', blank=True, null=True)
    position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    quote = models.TextField()

    def __str__(self):
        return self.name

class Homepage(SingletonModel):
    mentor_search_placeholder = models.CharField(max_length=255, default="Search for a mentor...")
    top_mentors = models.ManyToManyField(Mentor, related_name='top_mentors')
    company_logos = models.ManyToManyField(CompanyLogo, related_name='company_logos')
    categories = models.ManyToManyField(Category, related_name='categories')
    reviews = models.ManyToManyField(Review, related_name='homepage_reviews')
    faqs = models.ManyToManyField(FAQ, related_name='homepage_faqs')
    ceo_details = models.OneToOneField(CEO, on_delete=models.CASCADE, blank=True, null=True)
    section_title = models.CharField(max_length=255, default="Built for founders, marketers, and product people.")
    cards = models.ManyToManyField(CardSection, related_name='homepage_cards')
    def __str__(self):
        return "Homepage"

class CoreValue(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.heading

class BoardOfAdvisor(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='board_photos/')
    bio = models.TextField()

    def __str__(self):
        return self.name

class Teammates(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='team_photos/')
    bio = models.TextField()
    position = models.CharField(max_length=255, blank= True)
    linkedinurl = models.URLField(blank=True)
    def __str__(self):
        return self.name

class BlogCard(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blog_images/')
    url = models.URLField()

    def __str__(self):
        return self.title

class CTAButton(models.Model):
    text = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.text

class CTACard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    buttons = models.ManyToManyField(CTAButton)

    def __str__(self):
        return self.title

class AboutPage(SingletonModel):
    title = models.CharField(max_length=255)
    description = models.TextField()

    # New fields
    intro_image = models.ImageField(upload_to='intro_images/', blank=True, null=True)
    sub_intro_image1 = models.ImageField(upload_to='intro_images/', blank=True, null=True)
    sub_intro_image2 = models.ImageField(upload_to='intro_images/', blank=True, null=True)
    teammates = models.ManyToManyField(Teammates, related_name='about_teammates')
    about_us_story = models.TextField(blank=True, null=True)
    team_intro_text = models.TextField(blank=True, null=True)

    # Core Values (Heading + Description for each value)
    core_values = models.ManyToManyField(CoreValue, related_name='about_page_core_values')

    # Board of Advisors
    board_of_advisors = models.ManyToManyField(BoardOfAdvisor, related_name='about_page_board')

    # Call to Action (CTA) Card
    cta_card = models.OneToOneField(CTACard, on_delete=models.CASCADE, blank=True, null=True)

    # Blog Cards
    blogs = models.ManyToManyField(BlogCard, related_name='about_page_blogs')

    def __str__(self):
        return self.title

class ContactPage(SingletonModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.title

class PrivacyPolicyPage(SingletonModel):
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()

    def __str__(self):
        return self.title

class NewsletterPage(SingletonModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    signup_url = models.URLField()

    def __str__(self):
        return self.title

class CustomPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.JSONField()  # Use JSONField to store flexible content

    def __str__(self):
        return self.title

class MentoringCTA(models.Model):
    title = models.CharField(max_length=255, default="Get 1:1 Mentorship from Top Startup Experts")
    subtitle = models.CharField(max_length=255, default="India's 1st Startup Mentorship Platform")
    description = models.TextField(default="Don’t waste your time in Trial & Errors, Book 1:1 personalized session with Top experts in various industries.")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube URL for the video")
    top_mentors_count = models.IntegerField(default=100)
    happy_mentees_count = models.IntegerField(default=500)
    sessions_done_count = models.IntegerField(default=1000)
    rating_stars = models.FloatField(default=4.8)
    rating_label = models.CharField(max_length=255, default="Rated by Users")

    def __str__(self):
        return "Mentoring Call-to-Action Section"

class MenttalkCTA(SingletonModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='menttalk_images/')
    button_text = models.CharField(max_length=255)
    button_url = models.URLField()
    price = models.CharField(max_length=50)
    preorder_info = models.CharField(max_length=255)
    availability_info = models.CharField(max_length=255)
    extra_info = models.CharField(max_length=255)

    def __str__(self):
        return "Menttalk CTA"

class SocialLinks(models.Model):
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Social Links"

class Footer(models.Model):
    company_name = models.CharField(max_length=255)
    about_text = models.TextField()
    hashtag = models.CharField(max_length=255)
    email = models.EmailField()
    copyright = models.CharField(max_length=255)
    social_links = models.OneToOneField(SocialLinks, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return "Footer Section"

class FooterLink(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    footer = models.ForeignKey(Footer, related_name='links', on_delete=models.CASCADE)
    section = models.CharField(max_length=50, choices=[('company', 'Company'), ('quick', 'Quick Links'), ('compliance', 'Compliance')])

    def __str__(self):
        return f"{self.name} ({self.section})"