# Generated by Django 5.2.4 on 2025-07-12 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crops', '0003_systemmessage_created_by_userprofile_primary_crops'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosis',
            name='prevention',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='diagnosis',
            name='treatment',
            field=models.TextField(blank=True),
        ),
    ]
