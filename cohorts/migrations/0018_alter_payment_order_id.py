# Generated by Django 5.0 on 2024-08-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cohorts', '0017_alter_payment_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='order_id',
            field=models.CharField(default='b6b003fd-b77c-4b1f-8989-c04055ea41db', max_length=100, unique=True),
        ),
    ]
