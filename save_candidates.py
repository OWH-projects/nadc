from myproject.nadc.models import *

for obj in Expenditure.objects.exclude(raw_target=""):
    print obj.committee.standard_name
    obj.save()
