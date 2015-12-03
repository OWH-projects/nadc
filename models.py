from django.db import models
from django import forms
from django.db.models import *
from django.template.defaultfilters import slugify

class Entity(models.Model):
    nadcid = models.CharField(max_length=10, primary_key=True)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=80)
    standard_name = models.CharField(max_length=80)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    entity_type = models.CharField(max_length=15, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    occupation = models.TextField(null=True, blank=True)
    employer = models.TextField(null=True, blank=True)
    place_of_business = models.TextField(null=True, blank=True)
    dissolved_date = models.DateField(null=True, blank=True)
    registered_date = models.DateField(null=True, blank=True)

class Donation(models.Model):
    donor = models.ForeignKey(Entity, related_name="giver", null=True, blank=True)
    recipient = models.ForeignKey(Entity, related_name="getter", null=True, blank=True)
    cash = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    pledge = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind_desc = models.TextField(null=True, blank=True)
    donation_date = models.DateField()
    donation_year = models.CharField(max_length=4, default="")
    stance = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    donor_name = models.CharField(max_length=200, null=True, blank=True)
    
class Candidate(models.Model):
    cand_id = models.CharField(max_length=40, null=False, blank=False)
    cand_name = models.CharField(max_length=70, null=True, blank=True)
    stance = models.CharField(max_length=2, null=True, blank=True)
    committee = models.ForeignKey(Entity, related_name="candidate_detail")
    office_govt = models.CharField(max_length=100, null=True, blank=True)
    office_title = models.CharField(max_length=100, null=True, blank=True)
    office_dist = models.CharField(max_length=100, null=True, blank=True)
    donor_id = models.CharField(max_length=30, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    govslug = models.CharField(max_length=100, null=True, blank=True)
    def display_office(self):
        if len(self.office_dist) > 0:
            return "%s, %s" % (self.office_title, self.office_dist)
        else:
            return "%s" % (self.office_title)

    def save(self):
        self.govslug = '%s' % slugify(self.office_govt)
        print self.govslug
        super(Candidate, self).save()

class Loan(models.Model):
    committee = models.ForeignKey(Entity, null=True, blank=True, related_name="committee_lendee")
    lending_committee = models.ForeignKey(Entity, null=True, blank=True, related_name="committee_lender")
    lender_name = models.CharField(max_length=70, null=False, blank=False)
    lender_addr = models.CharField(max_length=70)
    loan_date = models.DateField()
    loan_amount = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    loan_repaid = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    loan_forgiven = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    paid_by_third_party = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    guarantor = models.CharField(max_length=70, null=True, blank=True)
    stance = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
class Expenditure(models.Model):
    committee = models.ForeignKey(Entity, related_name="committee_exp", null=True, blank=True) # (optional) committee doing the expending
    target_committee = models.ForeignKey(Entity, null=True, blank=True, related_name="committee_target_committee") # (optional) target committee, either being supported or opposed
    target_candidate = models.ForeignKey(Candidate, null=True, blank=True, related_name="committee_target_candidate")
    raw_target = models.CharField(max_length=100, null=True, blank=True) #(optional) raw text of target candidate or committee, to get sent to target_committee or target_candidate on save.
    payee_committee = models.ForeignKey(Entity, null=True, blank=True, related_name="committee_payee") #(optional) if group being paid has an id, it goes here
    payee = models.CharField(max_length=70, null=True, blank=True)
    payee_addr = models.CharField(max_length=70)
    exp_date = models.DateField()
    exp_purpose = models.CharField(max_length=200)
    amount = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    in_kind = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    stance = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    committee_exp_name = models.CharField(max_length=200, null=True, blank=True)
    def save(self):
        if len(self.raw_target) > 0:
            if Entity.objects.filter(nadcid=str(self.raw_target)).count() > 0:
                self.target_committee = Entity.objects.filter(nadcid=str(self.raw_target))[0]
            if Candidate.objects.filter(cand_id=str(self.raw_target)).count() > 0:
                self.target_candidate = Candidate.objects.filter(cand_id=str(self.raw_target))[0]
        super(Expenditure, self).save()

#This table stores information we want on people that does not exist in the database. Therefore, it's divorced from the normal database structure, with relationships that aren't defined explicitly in the data. Instead, they are handled through views. 
#Yes. This is gross.
class AdditionalInfo(models.Model):
    canonical = models.CharField(max_length=20, null=True, blank=True) #The canonical_id in the Entity table
    candidate = models.CharField(max_length=20, null=True, blank=True) #The candidate_id in the Candidate table
    mugshot = models.FileField(upload_to="nadc/mugs/")
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)

class Ballot(models.Model):
    nadcid = models.ForeignKey(Entity)
    ballot = models.CharField(max_length=80)
    ballot_type = models.CharField(max_length=5)
    stance = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

class SearchForm(forms.Form):
    searchterm = forms.CharField(label="Search term", max_length=75)
    from_date = forms.DateField(label="From date", required=False)
    to_date = forms.DateField(label="To date", required=False)

class AdvancedSearchForm(forms.Form):
    donor_name = forms.CharField(label="Donor name", max_length=75, required=False)
    recipient_name = forms.CharField(label="Recipient name", max_length=75, required=False)
    from_date = forms.DateField(label="From date", required=False)
    to_date = forms.DateField(label="To date", required=False)
    donor_city = forms.CharField(label="Donor city", max_length=75, required=False)
    recipient_city = forms.CharField(label="Recipient city", max_length=75, required=False)
    donor_state = forms.CharField(label="Donor state", max_length=75, required=False)
    giver_zip = forms.CharField(label="Donor ZIP code", max_length=75, required=False)
    recipient_zip = forms.CharField(label="Recipient ZIP code", max_length=75, required=False)
    expenditure_description = forms.CharField(label="Expenditure description", max_length=75, required=False)
    donations = forms.BooleanField(label="Search donations?", required=False, initial=True)
    loans = forms.BooleanField(label="Search loans?", required=False, initial=True)
    expenditures = forms.BooleanField(label="Search campaign expenditures?", required=False, initial=True)
    from_amount = forms.IntegerField(label="Minimum $", required=False, initial=0)
    to_amount = forms.IntegerField(label="Maxamim $", required=False, initial=2000000)

    
