import os
import csv
from fabric.api import *
#from myproject.nadc.models import *
from canonical.canonical import CANON

def test():
    for thing in CANON:
        print thing['origID']

def makeTables():
    print "Making lookup table ..."
    
def loadModels():
    print "Loading data into models ..."