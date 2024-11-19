from django.contrib import admin
from solo.admin import SingletonModelAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from io import TextIOWrapper
from .models import Homepage, AboutPage, ContactPage, PrivacyPolicyPage, NewsletterPage, CustomPage, CompanyLogo, Category, FAQ, CardSection, CEO
from .models import Teammates,MentoringCTA, MenttalkCTA,Footer, FooterLink, SocialLinks,AboutPage, CoreValue, BoardOfAdvisor, BlogCard, CTAButton, CTACard

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    change_list_template = "admin/category_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "This is not a valid CSV file.")
                return redirect("..")
            try:
                csv_reader = csv.reader(TextIOWrapper(csv_file, encoding='utf-8'))
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    Category.objects.create(
                        name=row[0],
                        description=row[1],
                        icon=row[2],
                        url=row[3]
                    )
                self.message_user(request, "CSV file uploaded successfully.")
            except Exception as e:
                self.message_user(request, f"Error uploading CSV: {str(e)}", level=messages.ERROR)
            return redirect("..")

        form = {}
        return render(request, "admin/csv_form.html", form)



class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1

class FooterAdmin(SingletonModelAdmin):
    inlines = [FooterLinkInline]
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ('heading', 'description')

class BoardOfAdvisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')

class TeammatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')

class BlogCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')

class CTAButtonAdmin(admin.ModelAdmin):
    list_display = ('text', 'url')

class CTACardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

admin.site.register(CoreValue, CoreValueAdmin)
admin.site.register(BoardOfAdvisor, BoardOfAdvisorAdmin)
admin.site.register(Teammates, TeammatesAdmin)
admin.site.register(BlogCard, BlogCardAdmin)
admin.site.register(CTAButton, CTAButtonAdmin)
admin.site.register(CTACard, CTACardAdmin)
admin.site.register(AboutPage, AboutPageAdmin)

admin.site.register(Footer, FooterAdmin)
admin.site.register(SocialLinks)
admin.site.register(Category, CategoryAdmin)

admin.site.register(MenttalkCTA, SingletonModelAdmin)
admin.site.register(MentoringCTA, SingletonModelAdmin)
admin.site.register(Homepage, SingletonModelAdmin)
admin.site.register(CompanyLogo)
admin.site.register(FAQ)
admin.site.register(CardSection)
admin.site.register(CEO)
admin.site.register(ContactPage, SingletonModelAdmin)
admin.site.register(PrivacyPolicyPage, SingletonModelAdmin)
admin.site.register(NewsletterPage, SingletonModelAdmin)
admin.site.register(CustomPage)
