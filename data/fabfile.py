import os
import csvkit
import fabric
from fabric.api import *
from fabric.operations import *
import collections
import pandas as pd
import datetime
from canonical.canonical import *

fabric.state.output.status = False

files_to_roll_through = [
        {'filename': 'formb1ab.txt', 'giver_col':4, 'getter_col':1, 'getter_name':0},
        {'filename': 'formb2a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb4a.txt', 'giver_col':2, 'getter_col':0},
        {'filename': 'formb5.txt', 'giver_col':7, 'getter_col':1, 'getter_name':0},
    ]
    
"""
A helper function to test whether a date sucks and is bad, and one to return "0.0" instead of a string.
"""

def validDate(datestring):
    try:
        return SHITDATES[datestring]
    except:
        high = datetime.datetime.now()
        low = datetime.datetime.strptime("1995-01-01", '%Y-%m-%d')
        try:
            # does it parse correctly?
            x = datetime.datetime.strptime(datestring, '%Y-%m-%d')
            # is the date between 1995 and today?
            if x > low and x < high:
                return datestring
            else:
                return "broke"
        except:
            return "broke"
    
def getFloat(i):
    if not i or i == "":
        return "0.0"
    else:
        return i

        
        
"""
This function rolls through the four main contribution files, extracts IDs for contributors and donors and returns a list of unique IDs for whatever type you specify. Set writeout to "yes" if you want to dump to a text file.

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
OK so this one returns a list of lists of IDs and types. Todo: incorporate into getUniqueList somehow?

--> fab getContribTypes
"""

def getContribTypes():
    masterlist = []
    with open("/home/apps/myproject/myproject/nadc/data/forma1.txt") as a1:
        reader = csvkit.reader(a1, delimiter="|")
        for row in reader:
            r = [row[0], row[6]]
            masterlist.append(r)

    with open("/home/apps/myproject/myproject/nadc/data/forma1.txt") as a1:
        reader = csvkit.reader(a1, delimiter="|")
        for row in reader:
            r = [row[0], row[6]]
            masterlist.append(r)
            
"""
This function creates a file of unique recipients -- this is our lookup table for the Getters model.

--> fab makeTables
"""

def dedupeGetters():
    toclean = pd.read_csv("/home/apps/myproject/myproject/nadc/data/forma1.txt", delimiter="|", low_memory=False)
    deduped = toclean.drop_duplicates(subset="Committee ID Number")
    deduped.to_csv('/home/apps/myproject/myproject/nadc/data/deduped-getters.txt', sep="|", header=False)
    with hide('running', 'stdout', 'stderr'):
        local('csvcut -d "|" -c 2,3,4,5,6,7,8 -x deduped-getters.txt | csvformat -D "|" | tr \'[:lower:]\' \'[:upper:]\' | sed \'s/,//g\' | sed \'s/\&AMP;/\&/g\' > toupload/getters.txt', capture=False)
        local('rm deduped-getters.txt', capture=False)


"""
This function does a lot of things. It:
- compares the list of unique recipients to the NADC lookup table (forma1.txt),
- finds any IDs that don't exist in the lookup table,
- captures a newline-separated grep string of the files in which those IDs are found,
- captures the name and ID of each in a list
- appends to the master recipient file

--> fab whoAintWeKnowAbout
"""
        
def whoAintWeKnowAbout():
    list_of_getters = getUniqueList("getter")
    committees_in_lookup = []
    with open("/home/apps/myproject/myproject/nadc/data/forma1.txt", "rb") as comm:
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
                grepstring = local('cd /home/apps/myproject/myproject/nadc/data && grep -m 1 "' + i + '" formb1ab.txt formb2a.txt formb4a.txt formb5.txt', capture=True)
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
This function parses the table of candidate information into something our database model can ingest.

--> fab parseCands
"""

def parseCands():
    getters = getUniqueList("getter")
    with open("/home/apps/myproject/myproject/nadc/data/forma1cand.txt", "rb") as f:
        reader = csvkit.reader(f, delimiter="|")
        reader.next()
        x = open("/home/apps/myproject/myproject/nadc/data/toupload/candidates.txt", "wb")
        for row in reader:
            if row[0] in getters:
                cand_id = row[2]
                comm_id = row[0]
                cand_name = ' '.join((row[4] + " " + row[5] + " " + row[3].strip()).split())
                print cand_name
                r = ["", cand_id, cand_name, comm_id ]
                x.write("|".join(r) + "\n")
        x.close()
    
    
"""
This function parses the table of loan information into something our database model can ingest.

--> fab parseLoans
"""

def parseLoans():
    getters = getUniqueList("getter")
    x = open("/home/apps/myproject/myproject/nadc/data/toupload/loans.txt", "wb")
    with open("/home/apps/myproject/myproject/nadc/data/formb1c.txt", "rb") as f:
        reader = csvkit.reader(f, delimiter="|")
        reader.next()
        for row in reader:
            if row[1] in getters:
                comm_id = row[1]
                lender_name = row[3].strip()
                lender_addr = row[4].strip()
                loan_date = row[5]
                loan_amount = row[6]
                loan_repaid = row[7]
                loan_forgiven = row[8]
                paid_by_third_party = row[9]
                guarantor = row[10]
                d = validDate(loan_date)
                if d != "broke":
                    r = ["", lender_name, lender_addr, loan_date, loan_amount, loan_repaid, loan_forgiven, paid_by_third_party, guarantor, comm_id]
                    x.write("|".join(r) + "\n")
    x.close()
    
  

"""
This function parses the table of expenditure information into something our database model can ingest.

--> fab parseExp
"""

def parseExp():
    getters = getUniqueList("getter")
    x = open("/home/apps/myproject/myproject/nadc/data/toupload/expenditures.txt", "wb")
    with open("/home/apps/myproject/myproject/nadc/data/formb1d.txt", "rb") as f:
        reader = csvkit.reader(f, delimiter="|")
        reader.next()
        for row in reader:
            if row[1] in getters:
                #Committee Name|Committee ID|Date Received|Payee Name|Payee Address|Expenditure Purpose|Expenditure Date|Amount|In-Kind
                comm_id = row[1]
                payee_name = row[3].strip()
                payee_addr = row[4].strip()
                exp_purpose = row[5].strip()
                exp_date = row[6]
                exp_amount = row[7]
                in_kind_amount = row[8]
                d = validDate(exp_date)
                if d != "broke":                    
                    r = ["", payee_name, payee_addr, exp_date, exp_purpose, exp_amount, in_kind_amount, comm_id]
                    x.write("|".join(r) + "\n")
    x.close()
  
"""
This guy makes a big ol' master table of donations to mow down.
--> fab StackItUp

Helper function lookItUp checks our canonical dict.
--> lookItUp("098SCO832", "canonicalid", "Ronald F. McDonald")
"""

def lookItUp(str, param, namefield):
    try:
        return CANON[str][param]
    except:
        if param == "canonicalid":
            return str
        else:
            return namefield
    
def stackItUp():
    headers = [
        "id",
        "giver_id",
        "canonical_id",
        "giver_name",
        "giver_canonical_name",
        "giver_address",
        "giver_city",
        "giver_state",
        "giver_zip",
        "giver_type",
        "getter_id",
        "cash_donation",
        "inkind_amount",
        "pledge_amount",
        "inkind_desc",
        "donation_date",
        "donation_year"
        ]
    
    rows_with_new_bad_dates = []
    alldonations = []
    typecomparison = {}
    
    #get IDs and types from Form A1
    with open("/home/apps/myproject/myproject/nadc/data/forma1.txt", "rb") as a1:
        reader = csvkit.reader(a1, delimiter="|")
        for row in reader:
            comm_id = row[0]
            comm_type = row[6]
            typecomparison[comm_id] = commm_type

    with open("formb1ab.txt", "rb") as b1ab, open("formb2a.txt", "rb") as b2a, open("formb4a.txt", "rb") as b4a, open("formb5.txt", "rb") as b5:
        
        #do b1ab
        reader_b1ab = csvkit.reader(b1ab, delimiter="|")
        reader_b1ab.next()
        for row in reader_b1ab:
            donor_id = row[4]
            donor_type = row[3]
            typecomparison[donor_id] = donor_type
            don_date = str(row[5])
            d = validDate(don_date)
            if d == "broke":
                dict = {}
                dict["giver_id"] = row[10]
                dict["getter_id"] = row[1]
                dict["source_table"] = "b1ab"
                dict["donation_date"] = don_date
                rows_with_new_bad_dates.append(dict)
            else:
                year = d.split("-")[0]
                if int(year) >= 1999:
                    name = ' '.join((row[10] + " " + row[11] + " " + row[9] + " " + row[12].strip()).split())                
                    r = ["", row[4], str(lookItUp(row[4],"canonicalid", name)), name, lookItUp(row[4],"canonicalname", name), str(row[13]), str(row[14]), str(row[15]), str(row[16]), str(row[3]), str(row[1]), getFloat(str(row[6])), getFloat(str(row[7])), getFloat(str(row[8])), "", d, year ]
                    standardrow = "|".join(r)
                    alldonations.append(standardrow)
        
        #do b5
        reader_b5= csvkit.reader(b5, delimiter="|")
        reader_b5.next()
        interimlist = []      
        for row in reader_b5:
            donor_id = row[7]
            donor_type = row[8]
            typecomparison[donor_id] = donor_type
            don_date = str(row[10])
            d = validDate(don_date)
            if d == "broke":
                dict = {}
                dict["giver_id"] = donor_id
                dict["getter_id"] = row[1]
                dict["source_table"] = "b5"
                dict["donation_date"] = don_date
                rows_with_new_bad_dates.append(dict)
            else:
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
            year = d.split("-")[0]
            if int(year) >= 1999:
                name = " ".join(row[15].split())
                r = [ "", donor_id, str(lookItUp(donor_id,"canonicalid",name)), str(lookItUp(donor_id,"canonicalname", name)), "", "", "", "", str(row[8]), str(row[1]), getFloat(cash), getFloat(inkind), getFloat(pledge), "", d, year ]
                standardrow = "|".join(r)
                alldonations.append(standardrow)
        
        #do b2a
        reader_b2a = csvkit.reader(b2a, delimiter="|")
        reader_b2a.next()
        for row in reader_b2a:
            donor_id = row[2]
            don_date = str(row[1])
            d = validDate(don_date)
            if d == "broke":
                dict = {}
                dict["giver_id"] = donor_id
                dict["getter_id"] = row[0]
                dict["source_table"] = "b2a"
                dict["donation_date"] = don_date
                rows_with_new_bad_dates.append(dict)
            else:
                try:
                    givertype = typecomparison[donor_id]
                except:
                    givertype = ""
                year = d.split("-")[0]
                if int(year) >= 1999:
                    name = " ".join(row[7].split())
                    r = [ "", donor_id, str(lookItUp(donor_id,"canonicalid",name)), name, str(lookItUp(donor_id,"canonicalname", name)), "", "", "", "", givertype, str(row[0]), getFloat(str(row[4])), getFloat(str(row[5])), getFloat(str(row[6])), "", d, year ]
                    standardrow = "|".join(r) + "\n"
                    alldonations.append(standardrow)
        
        #do b4a
        reader_b4a = csvkit.reader(b4a, delimiter="|")
        reader_b4a.next()
        for row in reader_b4a:
            donor_id = row[2]
            don_date = str(row[1])
            d = validDate(don_date)
            if d == "broke":
                dict = {}
                dict["giver_id"] = donor_id
                dict["getter_id"] = row[0]
                dict["source_table"] = "b4a"
                dict["donation_date"] = don_date
                rows_with_new_bad_dates.append(dict)
            else:
                try:
                    givertype = typecomparison[donor_id]
                except:
                    givertype = ""                        
                year = d.split("-")[0]
                if int(year) >= 1999:
                    name = " ".join(row[7].split())
                    r = [ "", donor_id, str(lookItUp(donor_id,"canonicalid",name)), name, str(lookItUp(donor_id,"canonicalname", name)), "", "", "", "", givertype, str(row[0]), getFloat(str(row[4])), getFloat(str(row[5])), getFloat(str(row[6])), "", d, year ]
                    standardrow = "|".join(r)
                    alldonations.append(standardrow)
        
    if len(rows_with_new_bad_dates) > 0:
        print "Got some records with bad dates. Go fix this in canonical.py and rerun parser.sh:"
        for thing in rows_with_new_bad_dates:
            print thing
        local("killall parser.sh", capture=False)
    else:
        with open("/home/apps/myproject/myproject/nadc/data/alldonations.txt", "wb") as f:
            f.write("|".join(headers) + "\n")
            for row in alldonations:
                final = str(row) + "\n"
                f.write(final)
        f.close()
    

"""
Homeboy here kicks out duplicate donations. Pandas!

--> fab dedupeDonations
"""

def dedupeDonations():
    toclean = pd.read_csv("/home/apps/myproject/myproject/nadc/data/alldonations.txt", delimiter="|", dtype={
        "id": object,
        "giver_id": object,
        "canonical_id": object,
        "giver_name": object,
        "giver_canonical_name": object,
        "giver_address": object,
        "giver_city": object,
        "giver_state": object,
        "giver_zip": object,
        "giver_type": object,
        "getter_id": object,
        "cash_donation": object,
        "inkind_amount": object,
        "pledge_amount": object,
        "inkind_desc": object,
        "donation_date": object,
        "donation_year": object
        }
    )
    deduped = toclean.drop_duplicates(subset=["giver_id", "donation_date", "getter_id", "cash_donation", "inkind_amount", "pledge_amount"])
    deduped.to_csv('/home/apps/myproject/myproject/nadc/data/deduped.csv', sep="|")
    with hide('running', 'stdout', 'stderr'):
        local('csvcut -d "|" -c id,cash_donation,inkind_amount,pledge_amount,inkind_desc,donation_date,giver_id,getter_id,donation_year deduped.csv | csvformat -D "|" | sed \'1d\' > toupload/donations.txt', capture=False)

        
"""
This one checks every donation record to return a unique list of contributors with the most complete and/or latest information. Rn it about 18 hours to run, so any performance tips welcome.

--> fab dedupeGivers
"""
        
def dedupeGivers():
    #Make a table of all givers, with dupes
    with hide('running', 'stdout', 'stderr'):
        local('csvsort -d "|" -c donation_date deduped.csv | csvcut -c giver_id,canonical_id,giver_name,giver_canonical_name,giver_address,giver_city,giver_state,giver_zip,giver_type | csvformat -D "|" | sed \'1d\' > rawgivers.txt', capture=False)
    
    #Now let's go through that and get a list of every NADC id
    rawgivers = csvkit.reader(open("rawgivers.txt", "rb"), delimiter="|")
    nadcids = []
    for row in rawgivers:
        nadcids.append(row[0])
    
    #Run set() to get uniques
    uniques = list(set(nadcids))

    #For every id, we need to find the most detailed row to keep. 
    mastergivers = []
    for idx, id in enumerate(uniques):
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
            #
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