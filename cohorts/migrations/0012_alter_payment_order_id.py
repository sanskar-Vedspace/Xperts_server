# Generated by Django 5.0 on 2024-08-28 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cohorts', '0011_alter_payment_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='order_id',
            field=models.CharField(default='def35903-95db-4efc-9692-795a52683c4a', max_length=100, unique=True),
        ),
    ]
