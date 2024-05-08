from django.contrib import admin

# Register your models here.
from .models import SiteModel

admin.site.register(SiteModel)