# Generated by Django 4.1.5 on 2023-01-30 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_contact_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='wallet_address',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
