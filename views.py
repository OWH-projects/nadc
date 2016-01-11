from models import *
from django.shortcuts import *
from django.db.models import *
from myproject.nadc.models import *
from django.http import HttpResponse
from django.db.models import F
from django.db import connection
import datetime
from last_updated import LAST_UPDATED
from django.views.generic import DetailView

DONATION_TOTAL = Donation.objects.count() + Expenditure.objects.count() + Loan.objects.count()

def Main(request):
    lastyear = datetime.datetime.now() - datetime.timedelta(days=365)
    monthlydonations = Donation.objects.filter(donation_date__gte=lastyear).values('donation_date').extra(select={'month': "EXTRACT(month FROM donation_date)"}).extra(select={'year': "EXTRACT(year FROM donation_date)"}).values('month', 'year').annotate(monthly_total=Sum("cash") + Sum("inkind"))
    last30donations = Donation.objects.filter(donation_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).annotate(totes=F('cash')+F('inkind')).order_by('-totes')
    last30donationstotal = last30donations.aggregate(Sum('totes'))
    monthlyexpenditures = Expenditure.objects.filter(exp_date__gte=lastyear).exclude(raw_target="").values('exp_date').extra(select={'month': "EXTRACT(month FROM exp_date)"}).extra(select={'year': "EXTRACT(year FROM exp_date)"}).values('month', 'year').annotate(monthly_total=Sum("amount") + Sum("in_kind"))
    monthlyadminexpenditures = Expenditure.objects.filter(exp_date__gte=lastyear).filter(raw_target="").values('exp_date').extra(select={'month': "EXTRACT(month FROM exp_date)"}).extra(select={'year': "EXTRACT(year FROM exp_date)"}).values('month', 'year').annotate(monthly_total=Sum("amount") + Sum("in_kind"))
    last30admin = Expenditure.objects.filter(exp_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).filter(raw_target="").annotate(totes=F('amount')+F('in_kind')).order_by('-totes')
    last30admintotal = last30admin.aggregate(Sum('totes'))
    last30targeted = Expenditure.objects.filter(exp_date__gte=datetime.datetime.now() - datetime.timedelta(days=30)).exclude(raw_target="").annotate(totes=F('amount')+F('in_kind')).order_by('-totes')
    last30targetedtotal = last30targeted.aggregate(Sum('totes'))
    governments = Candidate.objects.values('office_govt').distinct().order_by('office_govt')
    donations = Donation.objects.all()
    top10ind = donations.filter(donor_id__entity_type="I").values("donor_id__canonical", "donor_id__standard_name").annotate(totes=Sum("cash") + Sum("inkind")).order_by("-totes")[:10]
    topvolumeunique = Donation.objects.filter(donor_id__entity_type="I").values('donor_id__standard_name', 'donor_id__canonical').annotate(Count('recipient', distinct=True)).order_by('-recipient__count')[:10]
    toprecipients = Donation.objects.values('recipient_id__canonical', 'recipient_id__standard_name').annotate(totes=Sum("cash")).order_by("-totes")[:10]
    today = datetime.datetime.now()
    today_minus_30 = datetime.datetime.now() - datetime.timedelta(days=30)
    bigwigs = AdditionalInfo.objects.all()

    dictionaries = {'governments': governments, 'monthlydonations':monthlydonations, 'last30donations':last30donations, 'last30donationstotal': last30donationstotal, 'monthlyexpenditures': monthlyexpenditures, 'monthlyadminexpenditures':monthlyadminexpenditures, 'last30targeted': last30targeted, 'last30targetedtotal':last30targetedtotal, 'last30admin': last30admin, 'last30admintotal': last30admintotal, 'DONATION_TOTAL':DONATION_TOTAL, 'top10ind':top10ind, 'topvolumeunique':topvolumeunique, 'LAST_UPDATED': LAST_UPDATED, 'toprecipients': toprecipients, 'today':today, 'today_minus_30':today_minus_30, 'bigwigs': bigwigs, }
    return render_to_response('nadc/main.html', dictionaries)

def Govt(request, govslug):
    candidates = Candidate.objects.filter(govslug=govslug).order_by('office_title', 'office_dist', 'cand_name')
    dictionaries = {'candidates':candidates,}
    return render_to_response('nadc/govt.html', dictionaries)

def DatePage(request, startdate, enddate=None):
    startdate = "%s-%s-%s" % (startdate[4:], startdate[:2], startdate[2:4])
    startdate = datetime.datetime.strptime(startdate , '%Y-%m-%d')
    if enddate:
        enddate = "%s-%s-%s" % (enddate[4:], enddate[:2], enddate[2:4])
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    else:
        enddate = []
        
    if enddate:
        try:
            gives = Donation.objects.filter(donation_date__gte=startdate).filter(donation_date__lte=enddate).order_by("-donation_date")
        except:
            gives = []
        try:
            normal_expenditures = Expenditure.objects.filter(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
            ind_expenditures = Expenditure.objects.exclude(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
        except:
            normal_expenditures = []
            ind_expenditures = []
        try:
            loans = Loan.objects.filter(loan_date__gte=startdate).filter(loan_date__lte=enddate).order_by('-loan_date')
        except:
            loans = []
    else:
        try:
            gives = Donation.objects.filter(donation_date=startdate)
        except:
            gives = []
        try:
            normal_expenditures = Expenditure.objects.filter(raw_target="").filter(exp_date=startdate).order_by('-exp_date')
            ind_expenditures = Expenditure.objects.exclude(raw_target="").filter(exp_date=startdate).order_by('-exp_date')
        except:
            normal_expenditures = []
            ind_expenditures = []
        try:
            loans = Loan.objects.filter(loan_date=startdate).order_by('-loan_date')
        except:
            loans = []
    dictionaries = {'startdate':startdate, 'enddate':enddate,'gives': gives, 'normal_expenditures': normal_expenditures, 'ind_expenditures': ind_expenditures, 'loans': loans,'type':type}
    return render_to_response('nadc/datepage.html', dictionaries)

    
    
def DateJSON(request, startmonth, startday, startyear, endmonth=None, enddate=None, endyear=None, entity=None, type=None):

    startdate = "%s-%s-%s" % (startyear, startmonth, startday)
    
    if endmonth:
        enddate = "%s-%s-%s" % (endyear, endmonth, enddate)
    else:
        enddate = datetime.datetime.today().strftime("%Y-%m-%d")
    
    # Get any/all records of donations given, by entity if provided
    if entity:
        try:
            gives = Donation.objects.filter(donor__canonical=entity).filter(donation_date__gte=startdate).filter(donation_date__lte=enddate).order_by("-donation_date")
        except:
            gives = []
    else:
        try:
            gives = Donation.objects.filter(donation_date__gte=startdate).filter(donation_date__lte=enddate).order_by("-donation_date")
        except:
            gives = []

    # Get any/all records of donations received, by entity if provided
    if entity:
        try:
            gets = Donation.objects.filter(recipient__nadcid=entity).filter(donation_date__gte=startdate).filter(donation_date__lte=enddate).order_by("-donation_date")
        except:
            gets = []
    else:
        try:
            gets = Donation.objects.filter(donation_date__gte=startdate).filter(donation_date__lte=enddate).order_by("-donation_date")
        except:
            gets = []
        
        
    # Expenditures
    if entity:
        try:
            normal_expenditures = Expenditure.objects.filter(committee=entity).filter(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
            ind_expenditures = Expenditure.objects.filter(committee=entity).exclude(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
        except:
            normal_expenditures = []
            ind_expenditures = []
    else:
        try:
            normal_expenditures = Expenditure.objects.filter(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
            ind_expenditures = Expenditure.objects.exclude(raw_target="").filter(exp_date__gte=startdate).filter(exp_date__lte=enddate).order_by('-exp_date')
        except:
            normal_expenditures = []
            ind_expenditures = []

    # Loans
    if entity:
        try:
            loans = Loan.objects.filter(committee=entity).filter(loan_date__gte=startdate).filter(loan_date__lte=enddate).order_by('-loan_date')
        except:
            loans = []
    else:
        try:
            loans = Loan.objects.filter(loan_date__gte=startdate).filter(loan_date__lte=enddate).order_by('-loan_date')
        except:
            loans = []

    dictionaries = {'gives': gives, 'gets': gets, 'normal_expenditures': normal_expenditures, 'ind_expenditures': ind_expenditures, 'loans': loans,'type':type}
    return render_to_response('nadc/date.json', dictionaries, content_type='application/json')

    
def About(request):
    dictionaries = {}
    return render_to_response('nadc/about.html', dictionaries)
    
def Coverage(request):
    dictionaries = {}
    return render_to_response('nadc/coverage.html', dictionaries)

def Search(request):
    query = request.GET.get('q', '')
    exploded = query.split(" ")
    misc_qset = Q()
    entity_qset = Q()
    candidate_qset = Q()
    for term in exploded:
        entity_qset &= Q(standard_name__icontains=term) | Q(candidate_detail__cand_name__icontains=term) | Q(zip=term)

    for term in exploded:
        misc_qset &= Q(misc_name__icontains=term)
        
    for term in exploded:
        candidate_qset &= Q(cand_name__icontains=term)

    if query:
        entity_results = Entity.objects.values('canonical', 'standard_name').filter(entity_qset).distinct()
        candidate_results = Candidate.objects.filter(candidate_qset)
        misc_results = Misc.objects.filter(misc_qset)
    else:
        entity_results = []
        candidate_results = []
        misc_results = []

    dictionaries = { 'misc_results': misc_results, 'entity_results': entity_results, 'candidate_results': candidate_results, 'query': query, }
    return render_to_response('nadc/search.html', dictionaries)    
    
def EntityPage(request, id):
    alldonations = Donation.objects.filter(Q(recipient__nadcid=id)|Q(donor__canonical=id)).order_by('donation_date')    

    try:
        comm_candidates = Candidate.objects.filter(committee=id)
    except:
        comm_candidates = []       

    try:
        first = alldonations[0].donation_date
        mostrecent = alldonations.reverse()[0].donation_date
    except:
        first = []
        mostrecent = []
        
    truncate_date = connection.ops.date_trunc_sql('month', 'donation_date')

    name = Entity.objects.filter(canonical=id)[0]
    
    # Get any/all records of donations given by entity
    try:
        gives = Donation.objects.filter(donor__canonical=id).order_by("-donation_date")
    except:
        gives = []

    # Get any/all records of donations received by entity    
    try:
        gets = Donation.objects.filter(recipient__nadcid=id).order_by("-donation_date")
    except:
        gets = []
        
    # Expenditures
    try:
        normal_expenditures = Expenditure.objects.filter(committee=id).filter(raw_target="").order_by('-exp_date')
        ind_expenditures = Expenditure.objects.filter(committee=id).exclude(raw_target="").order_by('-exp_date')
    except:
        normal_expenditures = []
        ind_expenditures = []

    # Loans
    try:
        loans = Loan.objects.filter(committee=id).order_by('-loan_date')
    except:
        loans = []

    dictionaries = {'id': id, 'comm_candidates': comm_candidates, 'gives': gives, 'gets': gets, 'normal_expenditures': normal_expenditures, 'ind_expenditures': ind_expenditures, 'loans': loans, 'name':name, 'first':first, 'mostrecent':mostrecent, }
    
    return render_to_response('nadc/entity.html', dictionaries)

def DateWidget(request):
    dictionaries = {}
    return render_to_response('nadc/datewidget.html', dictionaries)
	
def ZipCode(request,zipcode):
    entities =  Entity.objects.filter(zip=zipcode)
    zip = zipcode

    dictionaries = { 'zip': zip, 'entities': entities, }    
    return render_to_response('nadc/zip.html', dictionaries)
    
class DonationDetailView(DetailView):
    model = Donation
