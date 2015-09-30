from myproject.nadc.models import *
from csvImporter.model import CsvDbModel

class Getter(CsvDbModel):
    class Meta:
        dbModel = Getter
        delimiter = "|"

class Giver(CsvDbModel):
    class Meta:
        dbModel = Giver
        delimiter = "|"

class Donation(CsvDbModel):
    class Meta:
        dbModel = Donation
        delimiter = "|"

