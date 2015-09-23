import os
import csv
from fabric.api import *
from fabric.operations import *
from canonical.canonical import CANON

"""
This function rolls through four of the main contribution files and extracts IDs for contributors and donors. Returns a list of unique IDs for whatever type you specify. Set writeout to "yes" if you want to dump the list to a text file.
"""

def getUniqueList(data_type, writeout="no"):
    files_to_roll_through = [
            {'filename': 'formb1ab.txt', 'giver_col':4, 'getter_col':1},
            {'filename': 'formb2a.txt', 'giver_col':2, 'getter_col':0},
            {'filename': 'formb4a.txt', 'giver_col':2, 'getter_col':0},
            {'filename': 'formb5.txt', 'giver_col':7, 'getter_col':1},
        ]
    ls = []    
    if data_type == "giver":
        for thing in files_to_roll_through:
            with open(thing['filename'], 'rb') as f:
                reader = csv.reader(f, delimiter="|")
                reader.next()
                for row in reader:
                    giver_id = row[thing['giver_col']]
                    ls.append(giver_id)
        uniq_ls = set(ls)
        if writeout == "yes":
            g = open("unique_contributor_ids.txt", "wb")
            for id in uniq_ls:
                g.write(id + "\n")
            g.close()
        return list(uniq_ls)
    elif data_type == "getter":
        for thing in files_to_roll_through:
            with open(thing['filename'], 'rb') as f:
                reader = csv.reader(f, delimiter="|")
                reader.next()
                for row in reader:
                    getter_id = row[thing['getter_col']]
                    ls.append(getter_id)
        uniq_ls = set(ls)
        if writeout == "yes":
            g = open("unique_recip_ids.txt", "wb")
            for id in uniq_ls:
                g.write(id + "\n")
            g.close()
        return list(uniq_ls)
    else:
        pass

"""
This function compares the list of unique getters to the NADC's top-level loopup committee table and returns a list of any discrepancies.

"""
        
def whoAintWeKnowAbout():
    list_of_getters = getUniqueList("getter")
    list_of_givers = getUniqueList("givers")
    derp = []
    with open("forma1.txt", "rb") as comm:
        reader = csv.reader(comm, delimiter="|")
        reader.next()
        for row in reader:
            getter_id = row[0]
            derp.append(getter_id)
        uniq_derp = set(derp)
    u_derp = list(uniq_derp)
    not_in_a1 = []
    for id in list_of_getters:
        if id not in u_derp:
            not_in_a1.append(id)
    if len(not_in_a1) > 0:
        print not_in_a1
    
        
        
            

def makeTables():
    print "Making lookup table ..."
    
def loadModels():
    print "Loading data into models ..."
    

    