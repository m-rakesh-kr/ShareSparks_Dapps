# Generated by Django 4.1.5 on 2023-02-24 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_alter_contentrewards_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='category',
        ),
        migrations.RemoveField(
            model_name='content',
            name='data',
        ),
        migrations.RemoveField(
            model_name='content',
            name='title',
        ),
    ]
