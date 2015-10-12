from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    donations = Donation.objects.filter(donation_date__gte='2005-01-01')
    top10ind = donations.filter(donor_id__contributor_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    top10pac = donations.filter(donor_id__contributor_type="C").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    top10cos = donations.filter(donor_id__contributor_type="").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    byyear = donations.values('donation_year').annotate(sum=Sum('cash'))
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind,'top10pac':top10pac,'top10cos':top10cos,'byyear':byyear,}
    return render_to_response('nadc/main.html', dictionaries)
    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)
    
# Committees share an id when listed as both donors and recipients. Our approach will be to have one page listing everything
# for every entity. So the thinking is: a handful of complex templates, rather than many possible views.
# Worth noting that this approach works because we only created canonical ids for individual donors. If we have to do the same for organizations, we might need a different approach.
# We shall see how this goes.
def Entity(request, entity):

    # Get any/all records of donations given by entity
    try:
        gives = Donation.objects.filter(donor=entity)
    except:
        gives = []

    # Get any/all records of donations received by entity    
    try:
        gets = Donation.objects.filter(recipient=entity)
    except:
        gets = []
    
    # Expenditures
    try:
        expenditures = Expenditure.objects.filter(commitee=entity)
    except:
        expenditures = []

    # Loans
    try:
        loans = Loan.objects.filter(committee=entity)
    except:
        loans = []
        
    dictionaries = {'gives': gives, 'gets': gets, 'expenditures': expenditures, 'loans': loans, }
    return render_to_response('nadc/entity.html', dictionaries)
    
