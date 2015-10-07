from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    top10ind = Donation.objects.filter(contributor_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    top10pac = Donation.objects.filter(contributor_type="C").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    top10cos = Donation.objects.filter(contributor_type="").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    byyear = Donation.objects.values('donation_year').annotate(sum=Sum('cash'))
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind,'top10pac':top10pac,'top10cos':top10cos,'byyear':byyear,}
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