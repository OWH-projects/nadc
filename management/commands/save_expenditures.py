from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from myproject.nadc.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        for obj in Expenditure.objects.exclude(raw_target=""):
            obj.save()
