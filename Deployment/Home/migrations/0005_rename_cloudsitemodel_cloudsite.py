# Generated by Django 5.0.4 on 2024-05-16 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0004_cloudsitemodel_remove_sitemodel_is_cloud_site'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CloudSiteModel',
            new_name='CloudSite',
        ),
    ]