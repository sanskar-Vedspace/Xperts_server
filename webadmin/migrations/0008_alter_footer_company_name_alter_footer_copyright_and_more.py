# Generated by Django 5.1.1 on 2024-09-12 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webadmin', '0007_footer_sociallinks_footerlink_footer_social_links'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footer',
            name='company_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='footer',
            name='copyright',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='footer',
            name='hashtag',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='footer',
            name='social_links',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webadmin.sociallinks'),
        ),
    ]
