from django.contrib import admin
from .models import *

@admin.register(AdditionalInfo)
class AdditionalInfoAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('canonical', 'candidate', 'name', 'title',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    search_fields = ['cand_name', 'cand_id']
#    list_filter = ('office_govt')
    list_display = ('cand_name', 'cand_id', 'committee_id')
    pass

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'standard_name', 'nadcid', 'canonical']
    list_display = ('standard_name', 'nadcid', 'canonical', 'name',)

