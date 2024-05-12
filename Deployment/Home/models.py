from django.db import models

# Create your models here.

class SiteModel(models.Model):

    # fields
    name = models.CharField(max_length=200, unique=True, help_text="The name of the Site. Site name should be unique.")
    kmaster_IP_address = models.GenericIPAddressField()
    knode1_IP_address = models.GenericIPAddressField()
    knode2_IP_address = models.GenericIPAddressField()
    username = models.CharField(max_length=50, blank=False, help_text="This username will be used to access the servers.")
    password = models.CharField(max_length=50, blank=False, help_text="The password for the username. Will be used to access servers.")
    dashboard_url = models.URLField(max_length=200)
    dashboard_username = models.CharField(max_length=50, blank=False, help_text="This username will be used to login to dashboards.")
    dashboard_password = models.CharField(max_length=50, blank=False, help_text="This password will be used to login to dashboards.")
    is_cloud_site = models.BooleanField(help_text="True if this is a cloud site else if on prem site then False.")

    def __str__(self): 
        return self.name 