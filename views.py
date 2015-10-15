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
        name = Giver.objects.filter(canonical=entity)[0]
    except:
        name = Getter.objects.filter(nadcid=entity)[0]

    # Get any/all records of donations given by entity
    try:
        gives = Donation.objects.filter(donor__canonical=entity)
        topgives = gives.values('recipient__name').annotate(totalcash=Sum('cash')).order_by('-totalcash')[:5]
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
        topgets = gets.values('donor__standard_name').annotate(totalcash=Sum('cash')).order_by('-totalcash')[:5]
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
        
    dictionaries = {'topgets': topgets, 'totalcashreceived': totalcashreceived, 'totalinkindreceived': totalinkindreceived, 'topgives': topgives, 'totalcashdonated': totalcashdonated, 'totalinkinddonated': totalinkinddonated,'gives': gives, 'gets': gets, 'expenditures': expenditures, 'loans': loans, 'name':name, }
    return render_to_response('nadc/entity.html', dictionaries)
    
