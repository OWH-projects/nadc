from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F
from django.db import connection
import datetime
from last_updated import LAST_UPDATED

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    donations = Donation.objects.all()
    top10ind = donations.filter(donor_id__entity_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    topvolumeraw = Donation.objects.filter(donor_id__entity_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient')).order_by('-recipient__count')[:10]
    topvolumeunique = Donation.objects.filter(donor_id__entity_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient', distinct=True)).order_by('-recipient__count')[:10]
    byyear = donations.values('donation_year').annotate(sum=Sum('cash'))
    dictionaries = {'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind,'topvolumeunique':topvolumeunique,'topvolumeraw':topvolumeraw,'byyear':byyear, 'LAST_UPDATED': LAST_UPDATED,}
    return render_to_response('nadc/main.html', dictionaries)
    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)



#This needs to be checked to ensure it rolls in candidate and ballotQs everywhere needed
def AdvancedSearch(request):
    if request.method == 'POST':
        mainform = AdvancedSearchForm(request.POST)
        if mainform.is_valid():
            donor = mainform.cleaned_data['donor_name']
            donor_exploded = donor.split(" ")
            recipient = mainform.cleaned_data['recipient_name']
            recipient_exploded = recipient.split(" ")
            donor_city = mainform.cleaned_data['donor_city']
            recipient_city = mainform.cleaned_data['recipient_city']
            giver_zip = mainform.cleaned_data['giver_zip']
            recipient_zip = mainform.cleaned_data['recipient_zip']
            expenditure_description = mainform.cleaned_data['expenditure_description']
            exp_exploded = expenditure_description.split(" ")
            donations_check = mainform.cleaned_data['donations']
            loans_check = mainform.cleaned_data['loans']
            from_amount = mainform.cleaned_data['from_amount']
            to_amount = mainform.cleaned_data['to_amount']
            expenditures_check = mainform.cleaned_data['expenditures']

            if donations_check == True:
                donation_qs = Q()
                for term in donor_exploded:
                    donation_qs &= Q(donor__standard_name__icontains=term) | Q(donor__candidate_detail__cand_name__icontains=term) | Q(donor__name__icontains=term)
                for term in recipient_exploded:
                    donation_qs &= Q(recipient__standard_name__icontains=term) | Q(recipient__candidate_detail__cand_name__icontains=term) | Q(recipient__name__icontains=term)
                

            if expenditures_check == True:
                expenditure_qs = Q()
                expterm_qs = Q()
                for term in donor_exploded:
                    expenditure_qs &= Q(committee__standard_name__icontains=term) | Q(payee__icontains=term) | Q(committee_exp_name__icontains=term)
                for term in exp_exploded:
                    expterm_qs &= Q(exp_purpose__icontains=term)

            if loans_check == True:
                loan_qs = Q()
                for term in donor_exploded:
                    loan_qs &= Q(lender_name__icontains=term) | Q(lending_committee__standard_name__icontains=term) | Q(lending_committee__candidate_detail__cand_name__icontains=term)
                for term in recipient_exploded:
                    loan_qs &= Q(committee__standard_name__icontains=term) | Q(committee__candidate_detail__cand_name__icontains=term)

            if mainform.cleaned_data['from_date']:
                from_date = mainform.cleaned_data['from_date']
            else:
                from_date = '1995-01-01'

            if mainform.cleaned_data['to_date']:
                to_date = mainform.cleaned_data['to_date']
            else:
                to_date = '2015-12-01'

            if donations_check == True:
                if donor or recipient:
                    donations = Donation.objects.filter(donation_qs).filter(donation_date__gte=from_date).filter(donation_date__lte=to_date).filter(donor__city__icontains=donor_city).filter(recipient__city__icontains=recipient_city).filter(donor__zip__icontains=giver_zip).filter(recipient__zip__icontains=recipient_zip).filter(Q(cash__gte=from_amount) | Q(inkind__gte=from_amount))
                else:
                    donations = Donation.objects.filter(donation_date__gte=from_date).filter(donation_date__lte=to_date).filter(donor__city__icontains=donor_city).filter(recipient__city__icontains=recipient_city).filter(donor__zip__icontains=giver_zip).filter(recipient__zip__icontains=recipient_zip).filter(Q(cash__gte=from_amount) | Q(inkind__gte=from_amount))
            else:
                donations = []
            
            if expenditures_check == True:
               expenditures = Expenditure.objects.filter(expenditure_qs).filter(exp_date__gte=from_date).filter(exp_date__lte=to_date).filter(expterm_qs).filter(payee_addr__icontains=recipient_city).filter(payee_addr__icontains=recipient_zip).filter(amount__gte=from_amount).filter(amount__lte=to_amount)
            else:
               expenditures = []

            if loans_check == True:
               loans = Loan.objects.filter(loan_qs).filter(loan_date__gte=from_date).filter(loan_date__lte=to_date).filter(loan_amount__lte=to_amount).filter(loan_amount__gte=from_amount).filter(lender_addr__icontains=donor_city).filter(lender_addr__icontains=giver_zip)
            else:
               loans = []
            dictionaries = {'loans': loans, 'expenditures': expenditures, 'donations':donations, 'mainform':mainform,}
            return render(request, 'nadc/advancedsearch.html', dictionaries)
        else:
            dictionaries = { 'mainform':mainform }
            return render(request, 'nadc/advancedsearch.html', dictionaries)
    else:
        mainform = AdvancedSearchForm()
        dictionaries = { 'mainform':mainform }
        return render(request, 'nadc/advancedsearch.html', dictionaries)

def Search(request):
    query = request.GET.get('q', '')
    exploded = query.split(" ")
    entity_qset = Q()
    candidate_qset = Q()
    for term in exploded:
        entity_qset &= Q(standard_name__icontains=term) | Q(candidate_detail__cand_name__icontains=term)

    for term in exploded:
        candidate_qset &= Q(cand_name__icontains=term)

    if query:
        entity_results = Entity.objects.filter(entity_qset)
        candidate_results = Candidate.objects.filter(candidate_qset)
    else:
        entity_results = []
        candidate_results = []

    dictionaries = { 'entity_results': entity_results, 'candidate_results': candidate_results, 'query': query, }
    return render_to_response('nadc/search.html', dictionaries)    



#def Search(request):
#    if request.method == 'POST':
#        mainform = SearchForm(request.POST)
#        if mainform.is_valid():
#            rawsearch = mainform.cleaned_data['searchterm']
#            rawsearch_exploded = rawsearch.split(" ")
#
#            expenditure_qs = Q()
#            for term in rawsearch_exploded:
#                expenditure_qs.add((
#                Q(payee__icontains=term) |
#                Q(committee__standard_name__icontains=term) |
#                Q(payee_committee__standard_name__icontains=term)),
#                expenditure_qs.connector)                
#
#            loan_qs = Q()
#            for term in rawsearch_exploded:    
#                loan_qs.add((
#                Q(lender_name__icontains=term) |
#                Q(committee__standard_name__icontains=term)),
#                loan_qs.connector)
#
#            donation_qs = Q()
#            for term in rawsearch_exploded:
#                donation_qs.add((
#                Q(donor__standard_name__icontains=term) | 
#                Q(recipient__standard_name__icontains=term)), 
#                donation_qs.connector)
#
#            if mainform.cleaned_data['from_date']:
#                from_date = mainform.cleaned_data['from_date']
#            else:
#                from_date = '1995-01-01'
#            if mainform.cleaned_data['to_date']:
#                to_date = mainform.cleaned_data['to_date']
#            else:
#                to_date = '2015-12-01'
#
#            donations = Donation.objects.filter(donation_qs).filter(donation_date__gte=from_date).filter(donation_date__lte=to_date)
#            expenditures = Expenditure.objects.filter(expenditure_qs).filter(exp_date__gte=from_date).filter(exp_date__lte=to_date)
#            loans = Loan.objects.filter(loan_qs).filter(loan_date__gte=from_date).filter(loan_date__lte=to_date)
#            dictionaries = {'loans': loans, 'expenditures': expenditures, 'donations':donations, 'rawsearch':rawsearch, 'mainform':mainform,}
#            return render(request, 'nadc/advancedsearch.html', dictionaries)
#    else:
#        mainform = SearchForm()
#    dictionaries = { 'mainform':mainform }
#    return render(request, 'nadc/search.html', dictionaries)

    
def EntityPage(request, id):

    try:
        comm_candidates = Candidate.objects.filter(committee=id)
    except:
        comm_candidates = []

    alldonations = Donation.objects.filter(Q(recipient__nadcid=id)|Q(donor__canonical=id)).order_by('donation_date')
    try:
        first = alldonations[0].donation_date
        mostrecent = alldonations.reverse()[0].donation_date
    except:
        first = []
        mostrecent = []
    truncate_date = connection.ops.date_trunc_sql('month', 'donation_date')
    
    try:
        name = Entity.objects.filter(canonical=id)[0]
    except:
        name = Candidate.objects.filter(cand_id=id)[0]

    # Get any/all records of donations given by entity
    try:
        gives = Donation.objects.filter(donor__canonical=id)
        allgives = gives.values('donation_date').annotate(total=Sum('cash') + Sum('inkind')).order_by('donation_date')
        topgives =  gives.values('recipient__name').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')[:5]
        givesbymonth = allgives.extra({'month':truncate_date})
        totalcashdonated = gives.aggregate(Sum('cash'))
        totalinkinddonated = gives.aggregate(Sum('inkind'))
    except:
        gives = []
        topgives = []
        totalcashdonated = []
        totalinkinddonated = []

    # Get any/all records of donations received by entity    
    try:
        gets = Donation.objects.filter(recipient__nadcid=id)
        allgets = gets.values('donation_date').annotate(total=Sum('cash') + Sum('inkind')).order_by('donation_date')
        topgets =  gets.values('donor__name').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')[:5]
        getsbymonth = allgets.extra({'month':truncate_date})
        totalcashreceived = gets.aggregate(Sum('cash'))
        totalinkindreceived = gets.aggregate(Sum('inkind'))
    except:
        gets = []
        topgets = []
        totalcashreceived = []
        totalinkindreceived = []        

    # Expenditures
    try:
        expenditures = Expenditure.objects.filter(committee=id)
        totalspent = expenditures.aggregate(Sum("amount"))
    except:
        expenditures = []
        totalspent = []

    # Loans
    try:
        loans = Loan.objects.filter(committee=id)
        totalborrowed = loans.aggregate(Sum("loan_amount"))
    except:
        loans = []
        totalborrowed - []
    
    dictionaries = {'totalspent':totalspent, 'getsbymonth':getsbymonth, 'givesbymonth':givesbymonth, 'allgives': allgives, 'comm_candidates': comm_candidates, 'topgets': topgets, 'totalcashreceived': totalcashreceived, 'totalinkindreceived': totalinkindreceived, 'topgives': topgives, 'totalcashdonated': totalcashdonated, 'totalinkinddonated': totalinkinddonated,'gives': gives, 'gets': gets, 'expenditures': expenditures, 'loans': loans, 'totalborrowed': totalborrowed, 'name':name, 'first':first,'mostrecent':mostrecent, }
    return render_to_response('nadc/entity.html', dictionaries)

