from django.db import models
from django.db.models import *
from django.template.defaultfilters import slugify

SOURCE_CHOICES = (
        ('B1AB', 'B1AB'),
        ('B2A', 'B2A'),
        ('B3', 'B3'),
        ('B4A', 'B4A'),
        ('B5', 'B5'),
    )

class Giver(models.Model):
    nadcid = models.CharField(max_length=10)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=65)
    standard_name = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    contributor_type = models.CharField(max_length=15, null=True, blank=True)

class Getter(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=65)
    standard_name = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    recipient_type = models.CharField(max_length=15, null=True, blank=True)

class Donation(models.Model):
    nadcid = models.ForeignKey(Giver)
    recipient = models.ForeignKey(Getter)
    cash = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    pledge = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind_desc = models.TextField(null=True, blank=True)
    date = models.DateField()
    source = models.CharField(max_length=5, choices=SOURCE_CHOICES)
