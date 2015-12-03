from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F
from django.db import connection
import datetime
from last_updated import LAST_UPDATED
import datetime

DONATION_TOTAL = Donation.objects.count()

def Main(request):
    lastyear = datetime.datetime.now() - datetime.timedelta(days=365)
    monthlydonations = Donation.objects.filter(donation_date__gte=lastyear).values('donation_date').extra(select={'month': "EXTRACT(month FROM donation_date)"}).values('month').annotate(monthly_total=Sum("cash") + Sum("inkind"))
    toplast30donations = Donation.objects.filter(donation_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).annotate(totes=F('cash')+F('inkind')).order_by('-totes')[:5]
    last30donationstotal = Donation.objects.filter(donation_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).aggregate(totes=Sum("cash") + Sum("inkind"))
    monthlyexpenditures = Expenditure.objects.filter(exp_date__gte=lastyear).exclude(raw_target="").values('exp_date').extra(select={'month': "EXTRACT(month FROM exp_date)"}).values('month').annotate(monthly_total=Sum("amount") + Sum("in_kind"))
    toplast30expenditures = Expenditure.objects.filter(exp_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).annotate(totes=F('amount')+F('in_kind')).order_by('-totes')[:5]
    last30expenditurestotal = Expenditure.objects.filter(exp_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).exclude(raw_target="").aggregate(totes=Sum("amount") + Sum("in_kind"))
    governments = Candidate.objects.values('office_govt').distinct().order_by('office_govt')
    donations = Donation.objects.all()
    top10ind = donations.filter(donor_id__entity_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash")).order_by("-totes")[:10]
    topvolumeraw = Donation.objects.filter(donor_id__entity_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient')).order_by('-recipient__count')[:10]
    topvolumeunique = Donation.objects.filter(donor_id__entity_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient', distinct=True)).order_by('-recipient__count')[:10]
    byyear = donations.values('donation_year').annotate(sum=Sum('cash'))
    toprecipients = Donation.objects.values('recipient_id__canonical', 'recipient_id__standard_name').annotate(totes=Sum("cash")).order_by("-totes")[:10]
    recentdonations = donations.filter(donation_date__gte=LAST_UPDATED+datetime.timedelta(-30), donation_date__lte=datetime.datetime.now()).annotate(totes=F('cash')+F('inkind')).order_by('-donation_date')

    dictionaries = {'governments': governments, 'monthlydonations':monthlydonations, 'toplast30donations':toplast30donations, 'last30donationstotal':last30donationstotal,'monthlyexpenditures': monthlyexpenditures,'toplast30expenditures': toplast30expenditures,'last30expenditurestotal': last30expenditurestotal, 'recentdonations':recentdonations,'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind,'topvolumeunique':topvolumeunique,'topvolumeraw':topvolumeraw,'byyear':byyear, 'LAST_UPDATED': LAST_UPDATED,'toprecipients': toprecipients,}
    return render_to_response('nadc/main.html', dictionaries)

def Govt(request, govslug):
    candidates = Candidate.objects.filter(govslug=govslug).order_by('office_title', 'office_dist', 'cand_name')
    dictionaries = {'candidates':candidates,}
    return render_to_response('nadc/govt.html', dictionaries)

    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)

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
        entity_results = Entity.objects.values('canonical', 'standard_name').filter(entity_qset).distinct()
        candidate_results = Candidate.objects.filter(candidate_qset)
    else:
        entity_results = []
        candidate_results = []

    dictionaries = { 'entity_results': entity_results, 'candidate_results': candidate_results, 'query': query, }
    return render_to_response('nadc/search.html', dictionaries)    
    
def EntityPage(request, id):

    #Test to see if we're dealing with a candidate record or not
    if Candidate.objects.filter(cand_id=id).count() > 0:
        candidatepage = True
    else:
        candidatepage = False
    
    #Candidate view
    if candidatepage == True:
        candidates = Candidate.objects.filter(cand_id=id)
        committees = Candidate.objects.filter(cand_id=id).values('committee', 'committee__standard_name').distinct()

        dictionaries = {'candidates':candidates, 'committees':committees,}
        return render_to_response('nadc/candidate.html', dictionaries)
    
    #Any single Entity view
    if candidatepage == False:
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
            gives = Donation.objects.filter(donor__canonical=id).order_by("-donation_date")
            allgives = gives.values('donation_date').annotate(total=Sum('cash') + Sum('inkind')).order_by('donation_date')
            groupedgives = gives.values('recipient__name', 'recipient__nadcid').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')
            topgives = groupedgives[:5]
            topgivestotal = 0
            for obj in topgives:
                topgivestotal = topgivestotal + obj['total']
            othergivestotal = allgives.aggregate(Sum('total'))['total__sum'] - topgivestotal
            givesbymonth = allgives.extra({'month':truncate_date})
            totalcashdonated = gives.aggregate(Sum('cash'))
            totalinkinddonated = gives.aggregate(Sum('inkind'))
        except:
            gives = []
            groupedgives= []
            allgives = []
            topgives = []
            othergivestotal = []
            givesbymonth = []
            totalcashdonated = []
            totalinkinddonated = []

        # Get any/all records of donations received by entity    
        try:
            gets = Donation.objects.filter(recipient__nadcid=id).order_by("-donation_date")
            allgets = gets.values('donation_date').annotate(total=Sum('cash') + Sum('inkind')).order_by('donation_date')
            groupedgets = gets.values('donor__standard_name', 'donor__canonical').annotate(total=Sum('cash') + Sum('inkind')).order_by('-total')
            topgets =  groupedgets[:5]
            topgetstotal = 0
            for obj in topgets:
                topgetstotal = topgetstotal + obj['total']
            othergetstotal = allgets.aggregate(Sum('total'))['total__sum'] - topgetstotal
            getsbymonth = allgets.extra({'month':truncate_date})
            totalcashreceived = gets.aggregate(Sum('cash'))
            totalinkindreceived = gets.aggregate(Sum('inkind'))
        except:
            gets = []
            topgets = []
            groupedgets = []
            topgetstotal = []
            totalcashreceived = []
            totalinkindreceived = []        
            othergetstotal = []
            getsbymonth = []
            
        # Expenditures
        try:
            normal_expenditures = Expenditure.objects.filter(committee=id).filter(raw_target="").order_by('-exp_date')
            normal_spent = normal_expenditures.aggregate(Sum("amount"))
            ind_expenditures = Expenditure.objects.filter(committee=id).exclude(raw_target="").order_by('-exp_date')
            ind_spent = ind_expenditures.aggregate(Sum("amount"))
        except:
            normal_expenditures = []
            normal_spent = []
            ind_expenditures = []
            ind_spent = []

        # Loans
        try:
            loans = Loan.objects.filter(committee=id).order_by('-loan_date')
            totalborrowed = loans.aggregate(Sum("loan_amount"))
        except:
            loans = []
            totalborrowed - []

        dictionaries = {'groupedgets': groupedgets, 'topgetstotal': topgetstotal, 'othergetstotal': othergetstotal, 'othergivestotal':othergivestotal, 'getsbymonth':getsbymonth, 'givesbymonth':givesbymonth, 'groupedgives': groupedgives, 'allgives': allgives, 'comm_candidates': comm_candidates, 'topgets': topgets, 'totalcashreceived': totalcashreceived, 'totalinkindreceived': totalinkindreceived, 'topgives': topgives, 'totalcashdonated': totalcashdonated, 'totalinkinddonated': totalinkinddonated,'gives': gives, 'gets': gets, 'normal_expenditures': normal_expenditures, 'normal_spent': normal_spent, 'ind_expenditures': ind_expenditures, 'ind_spent': ind_spent, 'loans': loans, 'totalborrowed': totalborrowed, 'name':name, 'first':first,'mostrecent':mostrecent, }
        return render_to_response('nadc/entity.html', dictionaries)

