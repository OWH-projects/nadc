from django.core.management.base import BaseCommand, CommandError
from myproject.nadc.models import *
from myproject.nadc import loadData

class Command(BaseCommand):
    help = 'Import data from raw NADC files into our whizbang models'

    def handle(self, *args, **options):
        
        #Load givers
        loadData.Giver.import_data(data = open("/home/apps/myproject/myproject/nadc/data/toupload/givers.txt"))
        loadData.Getter.import_data(data = open("/home/apps/myproject/myproject/nadc/data/toupload/getters.txt"))
        loadData.Donation.import_data(data = open("/home/apps/myproject/myproject/nadc/data/toupload/donations.txt"))
