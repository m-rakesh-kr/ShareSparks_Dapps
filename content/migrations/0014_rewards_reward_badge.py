# Generated by Django 4.1.5 on 2023-03-01 06:43

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_remove_content_category_remove_content_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rewards',
            name='reward_badge',
            field=cloudinary.models.CloudinaryField(default='v1677652935/ShareSparks-Rewards/jgmg1lis3yefnqzjpzoz.png', max_length=255, verbose_name='image'),
        ),
    ]
