# Generated by Django 5.0.4 on 2024-05-08 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitemodel',
            name='is_cloud_site',
            field=models.BooleanField(help_text='True if this is a cloud site else if on prem site then False.'),
        ),
    ]
