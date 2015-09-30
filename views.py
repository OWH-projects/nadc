from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F

DONATION_TOTAL = Donation.objects.all().count()

def Main(request):
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, }
    return render_to_response('nadc/main.html', dictionaries)
    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)
    
def Donor(request, donor):
    dictionaries = {}
    return render_to_response('nadc/donor.html', dictionaries)
    
def Recipient(request, recipient):
    dictionaries = {}
    return render_to_response('nadc/recipient.html', dictionaries)