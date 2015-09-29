import os
import csv
import fabric
from fabric.api import *
from fabric.operations import *
from canonical.canonical import CANON
import collections
import pandas as pd

files_to_roll_through = [
        {'filename': 'formb1ab.txt', 'giver_col':4, 'getter_col':1},
        {'filename': 'formb2a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb4a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb5.txt', 'giver_col':7, 'getter_col':1},
    ]

    

"""
This function rolls through four of the main contribution files and extracts IDs for contributors and donors and returns a list of unique IDs for whatever type you specify. Set writeout to "yes" if you want to dump to a text file.
--> fab getUniqueList:giver,yes

"""

def getUniqueList(data_type, writeout="no"):
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
This function compares the list of unique recipients to the NADC lookup table, forma1.txt, and writes out a list of any discrepancies to a text file.
--> fab whoAintWeKnowAbout

"""
        
def whoAintWeKnowAbout():
    list_of_getters = getUniqueList("getter")
    committees_in_lookup = []
    with open("forma1.txt", "rb") as comm:
        reader = csv.reader(comm, delimiter="|")
        reader.next()
        for row in reader:
            getter_id = row[0]
            committees_in_lookup.append(getter_id)
        uniq_comms = set(committees_in_lookup)
    not_in_a1 = []
    for id in list_of_getters:
        if id not in list(uniq_comms):
            not_in_a1.append(id)
    if len(not_in_a1) > 0:
        print "Found " + str(len(not_in_a1)) + " recipient IDs that weren't in the main lookup file."
        togrep = "\|".join(not_in_a1)
        local('grep "' + togrep + '" *.txt > toupload/committee_ids_we_aint_know_about.txt', capture=False)
    

    
"""
This guy makes a big ol' master table of donations to mow down.
--> fab StackItUp

Helper function lookItUp checks our canonical dict.
--> lookItUp("098SCO832", "canonicalid")

"""

def lookItUp(str, param):
    try:
        return CANON[str][param]
    except:
        return ""
    
def stackItUp():

    #f = open("donors_flattened.txt", "wb")
    headers = [ "giver_id", "canonical_id", "giver_name", "giver_canonical_name", "giver_address", "giver_city", "giver_state", "giver_zip", "giver_type", "getter_id", "cash_donation", "inkind_amount", "pledge_amount", "inkind_desc", "donation_date" ]
    
    with open("formb1ab.txt", "rb") as b1ab, open("formb2a.txt", "rb") as b2a, open("formb4a.txt", "rb") as b4a, open("formb5.txt", "rb") as b5:
        alldonations = []

        #do b1ab
        reader_b1ab = csv.reader(b1ab, delimiter="|")
        reader_b1ab.next()
        for row in reader_b1ab:
            name = ' '.join((row[10] + " " + row[11] + " " + row[9] + " " + row[12].strip()).split())
            r = [row[4], str(lookItUp(row[4],"canonicalid")), name, lookItUp(row[4],"canonicalname"), str(row[13]), str(row[14]), str(row[15]), str(row[16]), str(row[3]), str(row[1]), str(row[6]), str(row[7]), str(row[8]), "", str(row[5]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
        
        #do b5
        reader_b5= csv.reader(b5, delimiter="|")
        reader_b5.next()
        interimlist = []      
        for row in reader_b5:
            #In this table they got cute and added a lookup for the donation type. So we're finne handle that.
            if row[9] == "M":
                cash = row[11]
                inkind = ""
                pledge = ""
                interimlist.append(row)
            elif row[9] == "I":
                cash = ""
                inkind = row[11]
                pledge = ""
                interimlist.append(row)
            elif row[9] == "P":
                cash = ""
                inkind = ""
                pledge = row[11]
                interimlist.append(row)
            else:
                continue
        for row in interimlist:
            r = [ row[7], str(lookItUp(row[7],"canonicalid")), " ".join(row[15].split()), str(lookItUp(row[15],"canonicalname")), "", "", "", "", str(row[8]), str(row[1]), cash, inkind, pledge, "", str(row[10]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
                    
        #do b2a
        reader_b2a = csv.reader(b2a, delimiter="|")
        reader_b2a.next()
        for row in reader_b2a:
            r = [ row[2], str(lookItUp(row[2],"canonicalid")), " ".join(row[7].split()), str(lookItUp(row[7],"canonicalname")), "", "", "", "", "", str(row[0]), str(row[4]), str(row[5]), str(row[6]), "", str(row[1]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
           
        #do b4a
        reader_b4a = csv.reader(b4a, delimiter="|")
        reader_b4a.next()
        for row in reader_b4a:
            r = [ row[2], str(lookItUp(row[2],"canonicalid")), " ".join(row[7].split()), str(lookItUp(row[7],"canonicalname")), "", "", "", "", "", str(row[0]), str(row[4]), str(row[5]), str(row[6]), "", str(row[1]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)

    with open("/home/apps/myproject/myproject/nadc/data/alldonations.txt", "wb") as f:
        f.write("|".join(headers)+"\n")
        for row in alldonations:
            f.write(str(row))
    f.close()
    

def dedupeThatShizz():
    toclean = pd.read_csv("/home/apps/myproject/myproject/nadc/data/alldonations.txt", delimiter="|", low_memory=False)
    deduped = toclean.drop_duplicates()
    deduped.to_csv('/home/apps/myproject/myproject/nadc/data/deduped.csv', sep="|", quotechar="")
    
"""
This lil fella makes the main lookup tables for givers and getters.
--> fab makeTables

"""
    
def makeTables():
    f = open("toupload/getters.txt", "wb")
    x = open("toupload/getters_dupes.txt", "wb")
    ls = []
    with open("forma1.txt", "rb") as comm:
        reader = csv.reader(comm, delimiter="|")
        reader.next()
        for row in reader:
            ls.append(row[0])
            r = [row[0].strip(),"",row[1].strip(),"",row[2].strip(),row[3].strip(),row[4].strip(),row[5].strip(),row[6].strip()]
            f.write("|".join(r) + "\n")
    f.close()
    dupes = [item for item, count in collections.Counter(ls).items() if count > 1]
    if len(dupes) > 0:
        for i in dupes:
            x.write(i + "\n")
    x.close()
    
    master_giver_ls = []
    
    
    
    """
    now:
    - open each file
    - 
    
    """
    
    #list_of_getters = getUniqueList("getter")
    

    
    """
    with open("formXXXXXXX.txt", "rb") as f:
        reader = csv.reader(comm, delimiter="|")
        reader.next()
        for row in reader:
            print row
    """