from django.db import models
from django.db.models import *
from django.template.defaultfilters import slugify

class Giver(models.Model):
    nadcid = models.CharField(max_length=10, primary_key=True)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=65)
    standard_name = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    contributor_type = models.CharField(max_length=15, null=True, blank=True)

class Getter(models.Model):
    nadcid = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    recipient_type = models.CharField(max_length=15, null=True, blank=True)

class Donation(models.Model):
    donor = models.ForeignKey(Giver)
    recipient = models.ForeignKey(Getter)
    cash = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    pledge = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind_desc = models.TextField(null=True, blank=True)
    donation_date = models.DateField()
    donation_year = models.CharField(max_length=4, default="")
    
class Candidate(models.Model):
    cand_id = models.CharField(max_length=40, null=False, blank=False)
    cand_name = models.CharField(max_length=70, null=False, blank=False)
    committee = models.ForeignKey(Getter)

class Loan(models.Model):
    committee = models.ForeignKey(Getter)
    lender_name = models.CharField(max_length=70, null=False, blank=False)
    lender_addr = models.CharField(max_length=70)
    loan_date = models.DateField()
    loan_amount = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    loan_repaid = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    loan_forgiven = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    paid_by_third_party = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    guarantor = models.CharField(max_length=70, null=False, blank=True)
    