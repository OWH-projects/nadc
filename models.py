from django.db import models
from django.db.models import *
from django.template.defaultfilters import slugify

"""
class Example(models.Model):
    charfield = models.CharField(max_length=100, null=False, blank=False, primary_key=True)
    intfield = models.IntegerField(null=True, blank=True)
    boolfield = models.NullBooleanField()
    decimalfield = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    textfield = models.TextField(null=True, blank=True)

    class Meta:
        db_table = u'example'

    def __unicode__(self):
        return self.charfield

    def save(self):
        print self.charfield
        super(Example, self).save()
"""

SOURCE_CHOICES = (
        (B1AB, 'B1AB'),
        (B2A, 'B2A'),
        (B3, 'B3'),
        (B4A, 'B4A'),
        (B5, 'B5'),
    )

class Giver(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=65)
    standdardname = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    contributor_type = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)    

#class CanonicalLookup(models.Model):
#    orig_id = models.CharField(max_length=20, null=True, blank=True)
#    our_id = models.CharField(max_length=20, null=True, blank=True)
#    our_name = models.CharField(max_length=30)
    
class Getter(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    canonical = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=65)
    standardname = models.CharField(max_length=65)
    address = models.CharField(max_length=75, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)
    state = models.CharField(max_length=40, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    recipient_type = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=40, null=True, blank=True)

class Donation(models.Model):
    donor = models.ForeignKey(Giver)
    recipient = models.ForeignKey(Getter)
    cash = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkind = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    pledge = models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)
    inkinddesc = models.TextField(null=True, blank=True)
    date = models.DateField()
    source = models.CharField(max_length=5, choices=SOURCE_CHOICES)
    
    
