from django.db import migrations
from django.utils.text import slugify


def populate_cohort_slugs(apps, schema_editor):
    Cohort = apps.get_model('cohorts', 'Cohort')
    for cohort in Cohort.objects.all():
        if not cohort.slug:
            base_slug = slugify(cohort.name)
            slug = base_slug
            counter = 1
            while Cohort.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            cohort.slug = slug
            cohort.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cohorts', '0153_alter_cohort_end_date_alter_cohort_start_date'),
    ]

    operations = [
        migrations.RunPython(populate_cohort_slugs),
    ]
