from django.contrib import admin
from .models import AdditionalInfo


@admin.register(AdditionalInfo)
class AdditionalInfoAdmin(admin.ModelAdmin):
    pass