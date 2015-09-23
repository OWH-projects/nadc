from myproject.nadc.models import *
from csvImporter.model import CsvDbModel

class LoadGetter(CsvDbModel):
    class Meta:
        dbModel = Getter
        delimiter = "|"

class LoadGiver(CsvDbModel):
    class Meta:
        dbModel = Getter
        delimiter = "|"

class LoadDonation(CsvDbModel):
    class Meta:
        dbModel = Getter
        delimiter = "|"

