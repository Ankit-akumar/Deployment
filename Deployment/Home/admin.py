from django.contrib import admin

# Register your models here.
from .models import SiteModel, CloudSite

admin.site.register(SiteModel)
admin.site.register(CloudSite)