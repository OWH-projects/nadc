from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F
import datetime
from last_updated import LAST_UPDATED

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    donations = Donation.objects.all()
    top10ind = donations.filter(donor_id__contributor_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    topvolumeraw = Donation.objects.filter(donor_id__contributor_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient')).order_by('-recipient__count')[:10]
    topvolumeunique = Donation.objects.filter(donor_id__contributor_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient', distinct=True)).order_by('-recipient__count')[:10]
    byyear = donations.values('donation_year').annotate(sum=Sum('cash'))
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind,'topvolumeunique':topvolumeunique,'topvolumeraw':topvolumeraw,'byyear':byyear, 'LAST_UPDATED': LAST_UPDATED,}
    return render_to_response('nadc/main.html', dictionaries)
    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)

def Search(request):
    query = request.GET.get('q', '')
    exploded = query.split(" ")
    q_objects = Q()
    for term in exploded:
        q_objects &= Q(name__icontains=term)

    if query:
        qset = (
            q_objects
        )
        giver_results = Giver.objects.filter(qset)
        getter_results = Getter.objects.filter(qset)
        
    else:
        giver_results = []
        getter_results = []

    dictionaries = { 'giver_results': giver_results, 'getter_results': getter_results, 'query': query, }
    return render_to_response('nadc/search.html', dictionaries)    
    
# Committees share an id when listed as both donors and recipients. Our approach will be to have one page listing everything
# for every entity. So the thinking is: a handful of complex templates, rather than many possible views.
# Worth noting that this approach works because we only created canonical ids for individual donors. If we have to do the same for organizations, we might need a different approach.
# We shall see how this goes.
def Entity(request, entity):

    try:
        candidate = Candidate.objects.filter(committee=entity)
    except:
        candidate = []

    try:
        name = Giver.objects.filter(canonical=entity)[0]
    except:
        name = Getter.objects.filter(nadcid=entity)[0]

    # Get any/all records of donations given by entity
    try:
        gives = Donation.objects.filter(donor__canonical=entity)
        topgives =  gives.values('recipient__name').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')[:5]
        totalcashdonated = gives.aggregate(Sum('cash'))
        totalinkinddonated = gives.aggregate(Sum('inkind'))
    except:
        gives = []
        topgives = []
        totalcashdonated = []
        totalinkinddonated = []

    # Get any/all records of donations received by entity    
    try:
        gets = Donation.objects.filter(recipient__nadcid=entity)
        topgets =  gets.values('recipient__name').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')[:5]
        totalcashreceived = gets.aggregate(Sum('cash'))
        totalinkindreceived = gets.aggregate(Sum('inkind'))
    except:
        gets = []
        topgets = []
        totalcashreceived = []
        totalinkindreceived = []        
    
    # Expenditures
    try:
        expenditures = Expenditure.objects.filter(committee=entity)
    except:
        expenditures = []

    # Loans
    try:
        loans = Loan.objects.filter(committee=entity)
    except:
        loans = []
        
    dictionaries = {'candidate': candidate, 'topgets': topgets, 'totalcashreceived': totalcashreceived, 'totalinkindreceived': totalinkindreceived, 'topgives': topgives, 'totalcashdonated': totalcashdonated, 'totalinkinddonated': totalinkinddonated,'gives': gives, 'gets': gets, 'expenditures': expenditures, 'loans': loans, 'name':name, }
    return render_to_response('nadc/entity.html', dictionaries)
    
