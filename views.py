from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    #FIX LATER -- GROUP ON CANONICAL ONCE THAT ISH GETS SORTED
    top10 = Donation.objects.values("donor_id", "donor_id__name").annotate(totes=Sum("cash")).order_by("-cash")[:10]
    byyear = Donation.objects.values('donation_year').annotate(sum=Sum('cash'))
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, 'top10':top10,'byyear':byyear,}
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