import os
import csvkit
import fabric
from fabric.api import *
from fabric.operations import *
from canonical.canonical import CANON
import collections
import pandas as pd

fabric.state.output.status = False

files_to_roll_through = [
        {'filename': 'formb1ab.txt', 'giver_col':4, 'getter_col':1, 'getter_name':0},
        {'filename': 'formb2a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb4a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb5.txt', 'giver_col':7, 'getter_col':1, 'getter_name':0},
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
                reader = csvkit.reader(f, delimiter="|")
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
                reader = csvkit.reader(f, delimiter="|")
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
This function creates a file of unique recipients.
--> fab makeTables

"""
        
def dedupeGetters():
    toclean = pd.read_csv("/home/apps/myproject/myproject/nadc/data/forma1.txt", delimiter="|", low_memory=False)
    deduped = toclean.drop_duplicates(subset="Committee ID Number")
    deduped.to_csv('/home/apps/myproject/myproject/nadc/data/deduped-getters.txt', sep="|", header=False)
    with hide('running', 'stdout', 'stderr'):
        local('csvcut -H -d "|" -c 2,3,4,5,6,7,8 -x deduped-getters.txt | csvformat -D "|" | sed \'1d\' > toupload/getters.txt', capture=False)
        local('rm deduped-getters.txt', capture=False)


"""
This function does a lot of things. It:
- compares the list of unique recipients to the NADC lookup table (forma1.txt),
- finds any IDs that don't exist in the lookup table,
- captures a newline-separated grep string of the files in which those IDs are found,
- captures the name and ID of each 


--> fab whoAintWeKnowAbout

"""
        
def whoAintWeKnowAbout():
    list_of_getters = getUniqueList("getter")
    committees_in_lookup = []
    with open("forma1.txt", "rb") as comm:
        reader = csvkit.reader(comm, delimiter="|")
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
        ls= []
        done = []
        for i in not_in_a1:
            with hide('running', 'stdout', 'stderr'):
                grepstring = local('grep -m 1 "' + i + '" formb1ab.txt formb2a.txt formb4a.txt formb5.txt', capture=True)
                for dude in grepstring.split("\n"):
                    r = dude.split("|")
                    file = r[0].split(":")[0]
                    for x in files_to_roll_through:
                        if x['filename'] == file:
                            getter_id = r[x['getter_col']]
                            if getter_id not in done:
                                done.append(getter_id)
                                try:
                                    getter_name = r[x['getter_name']].split(":")[1].strip()
                                except:
                                    getter_name = ""
                                ls.append([getter_id, getter_name])
        with open("/home/apps/myproject/myproject/nadc/data/toupload/getters.txt", "ab") as x:
            for q in ls:
                comm_id = q[0]
                comm_name = q[1]
                outlist = [comm_id, comm_name, '', '', '', '', '']
                x.write("|".join(outlist) + "\n")

    
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

    headers = [ "giver_id", "canonical_id", "giver_name", "giver_canonical_name", "giver_address", "giver_city", "giver_state", "giver_zip", "giver_type", "getter_id", "cash_donation", "inkind_amount", "pledge_amount", "inkind_desc", "donation_date" ]
    
    with open("formb1ab.txt", "rb") as b1ab, open("formb2a.txt", "rb") as b2a, open("formb4a.txt", "rb") as b4a, open("formb5.txt", "rb") as b5:
        alldonations = []

        #do b1ab
        reader_b1ab = csvkit.reader(b1ab, delimiter="|")
        reader_b1ab.next()
        for row in reader_b1ab:
            name = ' '.join((row[10] + " " + row[11] + " " + row[9] + " " + row[12].strip()).split())
            r = [row[4], str(lookItUp(row[4],"canonicalid")), name, lookItUp(row[4],"canonicalname"), str(row[13]), str(row[14]), str(row[15]), str(row[16]), str(row[3]), str(row[1]), str(row[6]), str(row[7]), str(row[8]), "", str(row[5]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
        
        #do b5
        reader_b5= csvkit.reader(b5, delimiter="|")
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
                cash = row[11]
                inkind = ""
                pledge = ""
                interimlist.append(row)
        for row in interimlist:
            r = [ row[7], str(lookItUp(row[7],"canonicalid")), " ".join(row[15].split()), str(lookItUp(row[7],"canonicalname")), "", "", "", "", str(row[8]), str(row[1]), cash, inkind, pledge, "", str(row[10]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
                    
        #do b2a
        reader_b2a = csvkit.reader(b2a, delimiter="|")
        reader_b2a.next()
        for row in reader_b2a:
            r = [ row[2], str(lookItUp(row[2],"canonicalid")), " ".join(row[7].split()), str(lookItUp(row[2],"canonicalname")), "", "", "", "", "", str(row[0]), str(row[4]), str(row[5]), str(row[6]), "", str(row[1]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)
           
        #do b4a
        reader_b4a = csvkit.reader(b4a, delimiter="|")
        reader_b4a.next()
        for row in reader_b4a:
            r = [ row[2], str(lookItUp(row[2],"canonicalid")), " ".join(row[7].split()), str(lookItUp(row[2],"canonicalname")), "", "", "", "", "", str(row[0]), str(row[4]), str(row[5]), str(row[6]), "", str(row[1]) ]
            standardrow = "|".join(r) + "\n"
            alldonations.append(standardrow)

    with open("/home/apps/myproject/myproject/nadc/data/alldonations.txt", "wb") as f:
        f.write("|".join(headers)+"\n")
        for row in alldonations:
            f.write(str(row))
    f.close()
    

"""
Homeboy here kicks out duplicates. Pandas!
--> fab dedupeDonations

"""

def dedupeDonations():
    toclean = pd.read_csv("/home/apps/myproject/myproject/nadc/data/alldonations.txt", delimiter="|", low_memory=False)
    deduped = toclean.drop_duplicates()
    deduped.to_csv('/home/apps/myproject/myproject/nadc/data/deduped.csv', sep="|")
    local('csvcut -d "|" -c cash_donation,inkind_amount,pledge_amount,inkind_desc,donation_date,giver_id,getter_id deduped.csv | csvformat -D "|" > toupload/donations.txt', capture=False)
    
def dedupeGivers():
    #Make a table of all givers, with dupes
    local('csvsort -d "|" -c donation_date deduped.csv | csvcut -c giver_id,canonical_id,giver_name,giver_canonical_name,giver_address,giver_city,giver_state,giver_zip,giver_type | csvformat -D "|" > rawgivers.txt', capture=False)
    
    #Now let's go through that and get a list of every NADC id
    rawgivers = csvkit.reader(open("rawgivers.txt", "rb"), delimiter="|")
    nadcids = []
    for row in rawgivers:
        if row[0] not in nadcids:
            nadcids.append(row[0])
            
    #For every id, we need to find the most detailed row to keep. 
    mastergivers = []
    for idx, id in enumerate(nadcids):
        print str(idx)
        rawgivers = csvkit.reader(open("rawgivers.txt", "rb"), delimiter="|")
        #print "id number " + str(id)
        matches = []
        for row in rawgivers:
            if row[0] == id:
                matches.append(row)
        #print "We've got " + str(len(matches)) + " matches"
        for row in matches:
            master = None
            if len(row[3]) > 1 and len(row[4]) > 1 and len(row[5]) > 1:
                if master == None:
                    master = row
            else:
                if master == None:
                    master = row
        mastergivers.append(master)
    with open("/home/apps/myproject/myproject/nadc/data/toupload/givers.txt", "wb") as f:
        for row in mastergivers:
            #print row
            standardrow = "|".join(row) + "\n"
            f.write(standardrow)
    f.close()
    
def loadData():
    local('cd /home/apps/myproject/ && python2.7 manage.py load_nadc', capture=False)