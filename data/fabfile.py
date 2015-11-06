import os
import csvkit
import fabric
from fabric.api import *
from fabric.operations import *
import collections
import pandas as pd
import datetime
from canonical.canonical import *
import time
import re

fabric.state.output.status = False

"""
Helper functions.
"""

def validDate(datestring):
    """
    Check for known bad dates, invalid dates, dates in the future.
    """
    try:
        return SHITDATES[datestring]
    except:
        try:
            # is it a valid date?
            x = datetime.datetime.strptime(datestring, '%Y-%m-%d')
            # is the date before today?
            if x < datetime.datetime.now():
                return datestring
            else:
                return "broke"
        except:
            return "broke"

            
            
def getFloat(i):
    """
    Return a float or 0.0.
    """
    if not i or i == "":
        return "0.0"
    else:
        return i

        
def lookItUp(input, param, namefield):
    try:
        return str(CANON[input][param])
    except:
        if param == "canonicalid":
            return input
        else:
            return namefield

        
def getDate():
    """
    Parse the "last updated" date from a file in the NADC data dump.
    """
    q = open("/home/apps/myproject/myproject/nadc/last_updated.py", "wb")
    with open("/home/apps/myproject/myproject/nadc/data/DATE_UPDATED.TXT", "rb") as d:
        last_updated = d.readline().split(": ")[1].split(" ")[0].split("-")
        year = last_updated[0]
        month = last_updated[1]
        day = last_updated[2]
        q.write("import datetime\n\nLAST_UPDATED = datetime.date(" + year + ", " + month + ", " + day + ")")
    q.close()
        

def parseErrything():
    """
    Kicks out ready-to-upload data files:
        toupload/entity.txt
        toupload/candidate.txt
        toupload/donation.txt
        toupload/loan.txt
        toupload/expenditure.txt
        toupload/ballot.txt
    
    Forms we care about:
        A1: Most committees
        A1CAND: Candidates
        B1: Campaign statements for candidate or ballot question committees
        B1AB: Main donations table
        B1C: Loans to candidate or ballot question committees
        B1D: Expenditures by candidate or ballot question committees
        B2: Campaign statements for political party committees
        B2A: Contributions to candidate or ballot question committees
        B2B: Expenditures by party committees
        B4: Campaign statements for independent committees
        B4A: Donations to independent committees
        B4B1: Expenditures by independent committees
        B4B2: Federal and Out of State Disbursements
        B4B3: Administrative/Operating Disbursements
        B5: Late contributions
        B6: Reports of an independent expenditure or donation made by people or entities that are not registered as committees
        B6CONT: Contributions to committees by people who do not have an ID
        B6EXPEND: Expenditures made on behalf of committees by people who do not have an ID
        B7: Registration of corporations, unions and other associations
        B72: Direct contributions by corporations, unions and other associations
        B73: Indirect contributions by corporations, unions and other associations
        B9: Out of state expenditures/donations
        B9B: Out of state expenditures
        B11: Report of late independent expenditure    
    """
    
    delim = "|"
    id_master_list = []
    rows_with_new_bad_dates = []
    
    entities = open("/home/apps/myproject/myproject/nadc/data/toupload/entity-raw.txt", "wb")
    ballotq = open("/home/apps/myproject/myproject/nadc/data/toupload/ballot-raw.txt", "wb")
    candidates = open("/home/apps/myproject/myproject/nadc/data/toupload/candidate.txt", "wb")
    donations = open("/home/apps/myproject/myproject/nadc/data/toupload/donations-raw.txt", "wb")
    loans = open("/home/apps/myproject/myproject/nadc/data/toupload/loan.txt", "wb")
    expenditures = open("/home/apps/myproject/myproject/nadc/data/toupload/expenditure.txt", "wb")
    
    #write headers to files that get deduped by pandas or whatever
    donations_headers = [
        "db_id",
        "cash",
        "inkind",
        "pledge",
        "inkind_desc",
        "donation_date",
        "donor_id",
        "recipient_id",
        "donation_year",
        "notes",
        "stance",
        "donor_name"
        ]
    donations.write("|".join(donations_headers) + "\n")
    
    entities_headers = [
        "nadcid",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "entity_type",
        "notes",
        "employer",
        "occupation",
        "place_of_business",
        "dissolved_date",
        "date_we_care_about"
        ]
    entities.write("|".join(entities_headers) + "\n")

    ballot_headers = [
        "db_id",
        "name",
        "ballot_type",
        "stance",
        "nadc_id",
        "notes",
        "date_we_care_about"
        ]
    ballotq.write("|".join(ballot_headers) + "\n")
    
    print "\nPARSING RAW FILES"
    
    with open('forma1.txt', 'rb') as a1:
        """
        FormA1: Top-level table for committees. Supposed to include all committees in FormB1, FormB4, FormB2 reports, but we are going to be paranoid and not assume this is the case.
        
        Data is fed to Entity and BallotQ tables
        
        COLUMNS
        =======
        Committee ID Number|Committee Name|Committee Address|Committee City|Committee State|Committee Zip|Committee Type|Date Received|Postmark Date|Nature Of Filing|Ballot Question|Oppose Ballot Question|Ballot Type|Date over Theshold|Acronym|Separate Seg Political Fund ID|Separate Segregated Political Fund Name|SSPF Address|SSPF City|SSPF State|SSPF Zip|SSPF Type|Date Dissolved|Date of Next Election|Election Type|Won General|Won Primary
        """
        
        print "    forma1 ..."
        
        a1reader = csvkit.reader(a1, delimiter = delim)
        a1reader.next()
        
        for row in a1reader:
            a1_entity_id = row[0] #NADC ID
            if a1_entity_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(a1_entity_id)
                
                #Add to Entity
                a1_entity_name = ' '.join((row[1].upper().strip()).split()).replace('"',"") #Committee name
                a1_address = row[2] #Address
                a1_city = row[3] #City
                a1_state = row[4] #State
                a1_zip = row[5] #ZIP
                a1_entity_type = row[6].strip().upper() #Committee type
                a1_entity_dissolved = row[21] #Date dissolved
                a1_entity_date_of_thing_happening = row[7] #Date used to eval recency on dedupe
               
                """
                DB fields
                =========== 
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding a1_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                a1_entity_list = [
                    a1_entity_id,
                    a1_entity_name,
                    a1_address.upper(),
                    a1_city.upper(),
                    a1_state.upper(),
                    a1_zip,
                    a1_entity_type.upper(),
                    "",
                    "",
                    "",
                    "",
                    a1_entity_dissolved,
                    a1_entity_date_of_thing_happening,
                ]
                entities.write("|".join(a1_entity_list) + "\n")
                
                #is there a separate segregated political fund?
                if row[15] and row[15].strip() != "":
                    a1_sspf_id = row[15] #NADC ID
                    if a1_sspf_id not in SHITCOMMITTEES:
                        #Append ID to master list
                        id_master_list.append(a1_sspf_id)
                        
                        #Add to Entity
                        a1_sspf_name = row[16] #Committee name
                        a1_sspf_address = row[17] #Address
                        a1_sspf_city = row[18] #City
                        a1_sspf_state = row[19] #State
                        a1_sspf_zip = row[20] #ZIP
                        a1_sspf_type = row[21] #Committee type
                        a1_sspf_entity_date_of_thing_happening = row[7] #Date used to eval recency on dedupe
                        
                        a1_sspf_list = [
                            a1_sspf_id,
                            a1_sspf_name,
                            a1_sspf_address,
                            a1_sspf_city,
                            a1_sspf_state,
                            a1_sspf_zip,
                            a1_sspf_type,
                            "",
                            "",
                            "",
                            "",
                            a1_sspf_entity_date_of_thing_happening,
                        ]
                        entities.write("|".join(a1_sspf_list) + "\n")
                    
                #is this a ballot question?
                if row[6].upper().strip() == "B":
                    a1_nadc_id = row[0]
                    if a1_nadc_id not in SHITCOMMITTEES:
                        a1_ballot = ' '.join((row[10].upper().strip()).split()).replace('"',"")
                        a1_ballot_type = row[12]
                        a1_ballot_stance = row[11]
                        a1_ballot_date_of_thing_happening = row[7] #Date used to eval recency on dedupe
                        
                        ballotq_list = [
                            "",
                            a1_ballot,
                            a1_ballot_type,
                            a1_ballot_stance,
                            a1_nadc_id,
                            "",
                            a1_ballot_date_of_thing_happening,
                        ]
                        ballotq.write("|".join(ballotq_list) + "\n")

    
    with open('forma1cand.txt', 'rb') as a1cand:
        """
        FormA1CAND: Candidates connected to committees

        Data is fed to Candidate table
        
        COLUMNS
        =======
        Form A1 ID Number|Date Received|Candidate ID|Candidate Last Name|Candidate First Name|Candidate Middle Initial|Support/Oppose|Office Sought|Office Title|Office Description
        """
        
        print "    forma1cand ..."
        
        a1candreader = csvkit.reader(a1cand, delimiter = delim)
        a1candreader.next()

        for row in a1candreader:
            a1cand_id = row[2] #Candidate ID
            a1cand_committee_id = row[0] #Candidate Committee ID
            
            if a1cand_committee_id not in SHITCOMMITTEES:
                id_master_list.append(a1cand_committee_id)
                
                #Add to Entity

                a1cand_entity_name = ""
                a1cand_address = ""
                a1cand_city = ""
                a1cand_state = ""
                a1cand_zip = ""
                a1cand_entity_type = ""
                a1cand_entity_dissolved = ""
                a1cand_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe
               
                """
                DB fields
                =========== 
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding a1cand_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                a1cand_entity_list = [
                    a1cand_committee_id,
                    a1cand_entity_name,
                    a1cand_address,
                    a1cand_city,
                    a1cand_state,
                    a1cand_zip,
                    a1cand_entity_type,
                    "",
                    "",
                    "",
                    "",
                    a1cand_entity_dissolved,
                    a1cand_entity_date_of_thing_happening,
                ]
                entities.write("|".join(a1cand_entity_list) + "\n")
            
            if a1cand_committee_id not in SHITCOMMITTEES and a1cand_id not in SHITCOMMITTEES:
                #Append to Candidate
                a1cand_cand_last = row[3] #Last name
                a1cand_cand_first = row[4] #First name
                a1cand_cand_mid = row[5] #Middle initial
                a1cand_cand_full_name = " ".join([a1cand_cand_first, a1cand_cand_mid, a1cand_cand_last]) #Full name
                a1cand_cand_full_name = " ".join((a1cand_cand_full_name.upper().strip()).split()).replace('"',"")
                a1cand_stance = row[6] #Does committee support or oppose candidate? 0 = support, 1 = oppose            
                a1cand_office_sought = " ".join((row[7].upper().strip()).split()).replace('"',"") #Office sought
                a1cand_office_title = " ".join((row[8].upper().strip()).split()).replace('"',"") #Office title
                a1cand_office_desc = " ".join((row[9].upper().strip()).split()).replace('"',"") #Office description
        
                """
                DB fields
                =========
                db_id, cand_id, cand_name, committee_id, office_desc, office_sought, office_title, stance, donor_id, notes
                """
                a1cand_list = [
                    "",
                    a1cand_id,
                    a1cand_cand_full_name,
                    a1cand_committee_id,
                    a1cand_office_desc,
                    a1cand_office_sought,
                    a1cand_office_title,
                    a1cand_stance,
                    "",
                    ""
                ]
                candidates.write("|".join(a1cand_list) + "\n")
    
    
    with open('formb1.txt', 'rb') as b1:
        """
        FormB1: Campaign statements for candidate or ballot question committees

        Data is added to Entity
        
        COLUMNS
        =======
        Committee Name|Committee Address|Committee Type|Committee City|Committee State|Committee Zip|Committee ID Number|Date Last Revised|Last Revised By|Date Received|Postmark Date|Microfilm Number|Election Date|Type of Filing|Nature of Filing|Additional Ballot Question|Report Start Date|Report End Date|Field 1|Field 2A|Field 2B|Field 2C|Field 3|Field 4A|Field 4B|Field 5|Field 6|Field 7A|Field 7B|Field 7C|Field 7D|Field 8A|Field 8B|Field 8C|Field 8D|Field 9|Field 10|Field 11|Field 12|Field 13|Field 14|Field 15|Field 16|Field 17|Field 18|Field 19|Field 20|Field 21|Field 22|Field 23|Field 23|Field 24|Field 25|Field 26|Field 27|Adjustment|Total Unitemized Bills|Total Unpaid Bills|Total All Bills
        """
        
        print "    formb1 ..."
        
        b1reader = csvkit.reader(b1, delimiter = delim)
        b1reader.next()
        
        for row in b1reader:
            b1_entity_id = row[6]
            if b1_entity_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b1_entity_id)
                
                #Add to Entity
                b1_entity_name = ' '.join((row[0].upper().strip()).split()).replace('"',"") #Committee name
                b1_address = ' '.join((row[1].upper().strip()).split()).replace('"',"") #Address
                b1_city = ' '.join((row[3].upper().strip()).split()).replace('"',"") #City
                b1_state = ' '.join((row[4].upper().strip()).split()).replace('"',"") #State
                b1_zip = row[5].strip() #ZIP
                b1_entity_type = row[2].strip().upper() #Committee type
                b1_entity_date_of_thing_happening = row[9] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b1_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                b1_entity_list = [
                    b1_entity_id,                    
                    b1_entity_name,
                    b1_address,
                    b1_city,
                    b1_state,
                    b1_zip,
                    b1_entity_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b1_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b1_entity_list) + "\n")

    
    with open('formb1ab.txt', 'rb') as b1ab:
        """
        FormB1AB: Main donations table

        Data is added to Entity and Donation tables
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|Type of Contributor|Contributor ID|Contribution Date|Cash Contribution|In-Kind Contribution|Unpaid Pledges|Contributor Last Name|Contributor First Name|Contributor Middle Initial|Contributor Organization Name|Contributor Address|Contributor City|Contributor State|Contributor Zipcode
        """
        
        print "    formb1ab ..."
        
        b1abreader = csvkit.reader(b1ab, delimiter = delim)
        b1abreader.next()
        
        for row in b1abreader:
            b1ab_committee_id = row[1]
            b1ab_contributor_id = row[4]
            
            if b1ab_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b1ab_committee_id)
                
                #Add committee to Entity
                b1ab_committee_name = ' '.join((row[0].upper().strip()).split()).replace('"',"") #Committee name
                b1ab_committee_address = "" #Address
                b1ab_committee_city = "" #City
                b1ab_committee_state = "" #State
                b1ab_committee_zip = "" #ZIP
                b1ab_committee_type = "" #Committee type
                b1ab_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe
                
                """
                DB fields
                ===========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b1ab_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b1ab_committee_list = [
                    b1ab_committee_id,
                    b1ab_committee_name,
                    b1ab_committee_address,
                    b1ab_committee_city,
                    b1ab_committee_state,
                    b1ab_committee_zip,
                    b1ab_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b1ab_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b1ab_committee_list) + "\n")

            if b1ab_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b1ab_contributor_id)
                
                #Add contributor to Entity
                b1ab_contributor_last = row[9] #Contributor last name
                b1ab_contributor_first = row[10] #Contributor first name
                b1ab_contributor_mid = row[11] #Contributor middle name
                b1ab_contributor_org_name = row[12] #Contributor org name
                b1ab_concat_name = " ".join([b1ab_contributor_first, b1ab_contributor_mid, b1ab_contributor_last, b1ab_contributor_org_name])
                b1ab_contributor_name = ' '.join((b1ab_concat_name.upper().strip()).split()).replace('"',"") #Contributor name
                b1ab_contributor_address = row[13].upper().strip() #Address
                b1ab_contributor_city = row[14].upper().strip() #City
                b1ab_contributor_state = row[15].upper().strip() #State
                b1ab_contributor_zip = row[16] #ZIP
                b1ab_contributor_type = row[3].upper().strip() #Contributor type
                b1ab_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe
                
                """
               DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b1ab_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b1ab_contributor_list = [
                    b1ab_contributor_id,
                    b1ab_contributor_name,
                    b1ab_contributor_address,
                    b1ab_contributor_city,
                    b1ab_contributor_state,
                    b1ab_contributor_zip,
                    b1ab_contributor_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b1ab_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b1ab_contributor_list) + "\n")

            #Womp into donations
            if b1ab_contributor_id not in SHITCOMMITTEES and b1ab_committee_id not in SHITCOMMITTEES:
                #datetest
                b1ab_donation_date = row[5]
                b1ab_date_test = validDate(b1ab_donation_date)
                if b1ab_date_test == "broke":
                    b1ab_dict = {}
                    b1ab_dict["donor_id"] = row[10]
                    b1ab_dict["recipient_id"] = row[1]
                    b1ab_dict["lookup_name"] = ' '.join((row[0].upper().strip()).split()).replace('"',"")
                    b1ab_dict["source_table"] = "b1ab"
                    b1ab_dict["destination_table"] = "donation"
                    b1ab_dict["donation_date"] = b1ab_donation_date
                    rows_with_new_bad_dates.append(b1ab_dict)
                else:
                    b1ab_year = b1ab_date_test.split("-")[0]
                    if int(b1ab_year) >= 1999:
                        b1ab_cash = getFloat(str(row[6])) #cash                        
                        b1ab_inkind_amount = getFloat(str(row[7])) #inkind
                        b1ab_pledge_amount = getFloat(str(row[8])) #pledge
                        b1ab_inkind_desc = "" #in-kind description
                        
                        """
                        DB fields
                        =========
                        db_id, cash, inkind, pledge, inkind_desc, donation_date, donor_id, recipient_id, donation_year, notes, stance, donor_name
                        """
                        b1ab_donation_list = [                        
                            "",
                            b1ab_cash,
                            b1ab_inkind_amount,
                            b1ab_pledge_amount,
                            b1ab_inkind_desc,
                            b1ab_date_test,
                            b1ab_contributor_id,
                            b1ab_committee_id,
                            b1ab_year,
                            "",
                            "",
                            "",
                        ]
                        donations.write("|".join(b1ab_donation_list) + "\n")
    
    
    with open('formb1c.txt', 'rb') as b1c:
        """
        FormB1C: Loans to candidate or ballot question committees

        Data is added to Entity and Loan tables
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|Lender Name|Lender Address|Loan Date|Amount Received|Amount Repaid|Amount Forgiven|Paid by 3rd Party|Guarantor
        """
        
        print "    formb1c ..."
        
        b1creader = csvkit.reader(b1c, delimiter = delim)
        b1creader.next()
        
        for row in b1creader:
            b1c_committee_id = row[1]
            if b1c_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b1c_committee_id)
                
                #Add committee to Entity
                b1c_committee_name = ' '.join((row[0].upper().strip()).split()).replace('"',"") #Committee name
                b1c_committee_address = "" #Address
                b1c_committee_city = "" #City
                b1c_committee_state = "" #State
                b1c_committee_zip = "" #ZIP
                b1c_committee_type = "" #Committee type
                b1c_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b1c_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b1c_committee_list = [
                    b1c_committee_id,
                    b1c_committee_name,
                    b1c_committee_address,
                    b1c_committee_city,
                    b1c_committee_state,
                    b1c_committee_zip,
                    b1c_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b1c_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b1c_committee_list) + "\n")
                                
                #Womp loans into loan table
                b1c_lender_name = ' '.join((row[3].strip().upper()).split())
                b1c_lender_addr = row[4].upper().strip()
                b1c_loan_date = row[5]
                b1c_loan_amount = row[6]
                b1c_loan_repaid = row[7]
                b1c_loan_forgiven = row[8]
                b1c_paid_by_third_party = row[9]
                b1c_guarantor = row[10]
                b1c_loan_date_test = validDate(b1c_loan_date)
                if b1c_loan_date_test == "broke":
                    b1c_dict = {}
                    b1c_dict["donor_id"] = ""
                    b1c_dict["recipient_id"] = row[1]
                    b1c_dict["lookup_name"] = ' '.join((row[0].upper().strip()).split()).replace('"',"")
                    b1c_dict["source_table"] = "b1c"
                    b1c_dict["destination_table"] = "loans"
                    b1c_dict["donation_date"] = b1c_loan_date
                    rows_with_new_bad_dates.append(b1c_dict)
                else:
                    b1c_year = b1c_loan_date_test.split("-")[0]
                    if int(b1c_year) >= 1999:
                        
                        """
                        DB fields
                        ========
                        db_id, lender_name, lender_addr, loan_date, loan_amount, loan_repaid, loan_forgiven, paid_by_third_party, guarantor, committee_id, notes, stance, lending_committee_id
                        """
                        
                        b1c_loan_list = [
                            "", #DB ID
                            b1c_lender_name, #lender name
                            b1c_lender_addr, #lender address
                            b1c_loan_date_test, #loan date
                            b1c_loan_amount, #loan amount
                            b1c_loan_repaid, #amount repaid
                            b1c_loan_forgiven, #amount forgiven
                            b1c_paid_by_third_party, #amount covered by 3rd party
                            b1c_guarantor, #guarantor
                            b1c_committee_id, #committee ID
                            "", #notes field
                            "", #stance field
                            "", #lending committee ID
                        ]
                        loans.write("|".join(b1c_loan_list) + "\n")
    
    
    with open('formb1d.txt', 'rb') as b1d:
        """
        FormB1D: Expenditures by candidate or ballot question committees

        Data is added to Entity and Expenditure tables
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|Payee Name|Payee Address|Expenditure Purpose|Expenditure Date|Amount|In-Kind
        """
        
        print "    formb1d ..."
        
        b1dreader = csvkit.reader(b1d, delimiter = delim)
        b1dreader.next()
    
        for row in b1dreader:
            b1d_committee_id = row[1]
            if b1d_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b1d_committee_id)
                
                #Add committee to Entity
                b1d_committee_name = ' '.join((row[0].upper().strip()).split()).replace('"',"") #Committee name
                b1d_committee_address = "" #Address
                b1d_committee_city = "" #City
                b1d_committee_state = "" #State
                b1d_committee_zip = "" #ZIP
                b1d_committee_type = "" #Committee type
                b1d_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b1d_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                
                b1d_committee_list = [
                    b1d_committee_id,
                    b1d_committee_name,
                    b1d_committee_address,
                    b1d_committee_city,
                    b1d_committee_state,
                    b1d_committee_zip,
                    b1d_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b1d_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b1d_committee_list) + "\n")
                
                # womp expenditures in there
                b1d_exp_date = row[6]
                b1d_exp_date_test = validDate(b1d_exp_date)
                if b1d_exp_date_test == "broke":
                    b1d_dict = {}
                    b1d_dict["donor_id"] = ""
                    b1d_dict["recipient_id"] = row[1]
                    b1d_dict["lookup_name"] = ' '.join((row[0].upper().strip()).split()).replace('"',"")
                    b1d_dict["source_table"] = "b1d"
                    b1d_dict["destination_table"] = "expenditures"
                    b1d_dict["donation_date"] = b1d_exp_date
                    rows_with_new_bad_dates.append(b1d_dict)
                else:
                    b1d_year = b1d_exp_date_test.split("-")[0]
                    if int(b1d_year) >= 1999:
                        b1d_payee = ' '.join((row[3].upper().strip()).split()).replace('"',"")
                        b1d_address = ' '.join((row[4].upper().strip()).split()).replace('"',"")
                        b1d_purpose = ' '.join((row[5].strip()).split()).replace('"',"")
                        b1d_amount = row[7]
                        b1d_inkind = row[8]
                        
                        """
                        DB fields
                        =========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b1d_exp_list = [
                            "",
                            b1d_payee,
                            b1d_address,
                            b1d_exp_date_test,
                            b1d_purpose,
                            b1d_amount,
                            b1d_inkind,
                            b1d_committee_id,
                            "",
                            "",
                            "",
                            "",
                        ]
                        expenditures.write("|".join(b1d_exp_list) + "\n")

    
    with open('formb2.txt', 'rb') as b2:
        """
        FormB2: Campaign statements for political party committees

        Data is added to Entity
        
        COLUMNS
        =======
        Committee Name|Committee Address|Committee City|Committee State|Committee Zip|Committee ID|Date Received|Date Last Revised|Last Revised By|Postmark Date|Microfilm Number|Election Date|Type of Filing|Nature Of Filing|Report Start Date|Report End Date|Financial Activity|Report ID
        """
        
        print "    formb2 ..."
        
        b2reader = csvkit.reader(b2, delimiter = delim)
        b2reader.next()
        
        for row in b2reader:
            b2_committee_id = row[5]
            if b2_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b2_committee_id)
                
                #Add committee to Entity
                b2_committee_name = ' '.join((row[0].upper().strip()).split()).replace('"',"") #Committee name
                b2_committee_address = ' '.join((row[1].upper().strip()).split()).replace('"',"") #Address
                b2_committee_city = ' '.join((row[2].upper().strip()).split()).replace('"',"") #City
                b2_committee_state = ' '.join((row[3].upper().strip()).split()).replace('"',"") #State
                b2_committee_zip = row[4] #ZIP
                b2_committee_type = "" #Committee type
                b2_entity_date_of_thing_happening = row[6] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b2_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b2_committee_list = [
                    b2_committee_id,
                    b2_committee_name,
                    b2_committee_address,
                    b2_committee_city,
                    b2_committee_state,
                    b2_committee_zip,
                    b2_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b2_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b2_committee_list) + "\n")
    
    
    with open('formb2a.txt', 'rb') as b2a:
        """
        FormB2A: Contributions to candidate or ballot question committees

        Data is added to Entity (probably uneccesarily) and Donation
        
        COLUMNS
        =======
        Committee ID|Date Received|Contributor ID|Contribution Date|Cash Contribution|In-Kind Contribution|Unpaid Pledges|Contributor Name
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb2a ..."
        
        b2areader = csvkit.reader(b2a, delimiter = delim)
        b2areader.next()
        
        for row in b2areader:
            b2a_committee_id = row[0]
            b2a_contributor_id = row[2]
            
            if b2a_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b2a_committee_id)
                
                #Add committee to Entity
                b2a_committee_name = "" #Committee name
                b2a_committee_address = "" #Address
                b2a_committee_city = "" #City
                b2a_committee_state = "" #State
                b2a_committee_zip = "" #ZIP
                b2a_committee_type = "" #Committee type
                b2a_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b2a_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b2a_committee_list = [
                    b2a_committee_id,
                    b2a_committee_name,
                    b2a_committee_address,
                    b2a_committee_city,
                    b2a_committee_state,
                    b2a_committee_zip,
                    b2a_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b2a_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b2a_committee_list) + "\n")
                
            if b2a_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b2a_contributor_id)
                
                #Add contributor to Entity
                b2a_contributor_name = ' '.join((row[7].upper().strip()).split()).replace('"',"") #Contributor name
                b2a_contributor_address = "" #Address
                b2a_contributor_city = "" #City
                b2a_contributor_state = "" #State
                b2a_contributor_zip = "" #ZIP
                b2a_contributor_type = "" #Contributor type
                b2a_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b2a_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b2a_contributor_list = [
                    b2a_contributor_id,
                    b2a_contributor_name,
                    b2a_contributor_address,
                    b2a_contributor_city,
                    b2a_contributor_state,
                    b2a_contributor_zip,
                    b2a_contributor_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b2a_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b2a_contributor_list) + "\n")
    
    
    with open('formb2b.txt', 'rb') as b2b:
        """
        FormB2B: Expenditures by party committees on behalf of other committees

        Data is added to Entity and Expenditure
        
        COLUMNS
        =======
        Committee ID|Date Received|Committee ID Expenditure is For|Support/Oppose|Nature of Expenditure|Expenditure Date|Amount|Description|Line ID|Committee Name Expenditure is For
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb2b ..."
        
        b2breader = csvkit.reader(b2b, delimiter = delim)
        b2breader.next()
        
        for row in b2breader:
            b2b_committee_id = row[0]
            b2b_beneficiary_id = row[2]
            
            if b2b_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b2b_committee_id)
                
                #Add committee to Entity
                b2b_committee_name = "" #Committee name
                b2b_committee_address = "" #Address
                b2b_committee_city = "" #City
                b2b_committee_state = "" #State
                b2b_committee_zip = "" #ZIP
                b2b_committee_type = "" #Committee type
                b2b_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b2b_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b2b_committee_list = [
                    b2b_committee_id,
                    b2b_committee_name,
                    b2b_committee_address,
                    b2b_committee_city,
                    b2b_committee_state,
                    b2b_committee_zip,
                    b2b_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b2b_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b2b_committee_list) + "\n")
            
            if b2b_beneficiary_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b2b_beneficiary_id)
                
                #Add beneficiary to Entity
                b2b_beneficiary_name = ' '.join((row[9].upper().strip()).split()).replace('"',"") #Beneficiary name
                b2b_beneficiary_address = "" #Address
                b2b_beneficiary_city = "" #City
                b2b_beneficiary_state = "" #State
                b2b_beneficiary_zip = "" #ZIP
                b2b_beneficiary_type = "" #Committee type
                b2b_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b2b_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b2b_beneficiary_list = [
                    b2b_beneficiary_id,
                    b2b_beneficiary_name,
                    b2b_beneficiary_address,
                    b2b_beneficiary_city,
                    b2b_beneficiary_state,
                    b2b_beneficiary_zip,
                    b2b_beneficiary_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b2b_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b2b_beneficiary_list) + "\n")
    
            if b2b_committee_id not in SHITCOMMITTEES and b2b_beneficiary_id not in SHITCOMMITTEES:
                # womp expenditures in there
                b2b_exp_date = row[5]
                b2b_exp_date_test = validDate(b2b_exp_date)
                if b2b_exp_date_test == "broke":
                    b2b_dict = {}
                    b2b_dict["donor_id"] = row[0]
                    b2b_dict["recipient_id"] = row[2]
                    b2b_dict["lookup_name"] = ' '.join((row[9].upper().strip()).split()).replace('"',"")
                    b2b_dict["source_table"] = "b2b"
                    b2b_dict["destination_table"] = "expenditures"
                    b2b_dict["donation_date"] = b2b_exp_date
                    rows_with_new_bad_dates.append(b2b_dict)
                else:
                    b2b_year = b2b_exp_date_test.split("-")[0]
                    if int(b2b_year) >= 1999:
                        b2b_payee = ""
                        b2b_address = ""
                        b2b_purpose = ' '.join((row[7].strip()).split()).replace('"',"")
                        b2b_stance = row[3].strip().upper()
                        b2b_recipient_committee_id = row[2]
                        
                        #What type of expenditure was it? D=Direct, K=In-kind, I=Independent Expenditure
                        if row[4].upper().strip() == "K":
                            b2b_amount = ""
                            b2b_inkind = row[6]
                        else:
                            b2b_amount = row[6]
                            b2b_inkind = ""
                        
                        """
                        DB fields
                        =========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b2b_exp_list = [
                            "",
                            b2b_payee,
                            b2b_address,
                            b2b_exp_date_test,
                            b2b_purpose,
                            b2b_amount,
                            b2b_inkind,
                            b2b_committee_id,
                            b2b_stance,
                            "",
                            b2b_beneficiary_id,
                            "",
                        ]
                        expenditures.write("|".join(b2b_exp_list) + "\n")
            
            
    with open('formb4.txt', 'rb') as b4:
        """
        FormB4: Campaign statements for independent committees

        Data is added to Entity
        
        COLUMNS
        =======
        Committee Name|Committee Address|Committee Type|Committee City|Committee State|Committee Zip|Committee ID|Date Recevied|Date Last Revised|Last Revised By|Postmark Date|Microfilm Number|Election Date|Type of Filing|Nature of Filing|Report Start Date|Report End Date|Nature of Committee|Field 1|Field 2A|Field 2B|Field 2C|Field 2D|Field 3|Field 4|Field 5|Field 6|Field 7|Field 8|Field 9|Field 10|Field 11A|Field 11B|Field 11C|Field 11D|Field 12|Field 13|Field 14|Field 15|Field 16|Field 17|Field 18|Field 19|Field 20|Field 21|Field 22|Field 23|Field 24|Field 25|Field 26|Description|Report ID        
        """
        
        print "    formb4 ..."
        
        b4reader = csvkit.reader(b4, delimiter = delim)
        b4reader.next()
        
        for row in b4reader:
            b4_committee_id = row[6]
            if b4_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4_committee_id)
                
                #Add committee to Entity
                b4_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b4_committee_address = ' '.join((row[1].strip().upper()).split()).replace('"',"") #Address
                b4_committee_city = ' '.join((row[3].strip().upper()).split()).replace('"',"") #City
                b4_committee_state = ' '.join((row[4].strip().upper()).split()).replace('"',"") #State
                b4_committee_zip = row[5] #ZIP
                b4_committee_type = row[2].upper().strip() #Committee type (C=Candidate Committee, B=Ballot Question, P=Political Action Committee, T=Political Party Committee, I or R = Independent Reporting Committee, S=Separate Segregated Political Fund Committee)
                b4_entity_date_of_thing_happening = row[7] #Date used to eval recency on dedupe

                """
                DB fields
                ==========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b4_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4_committee_list = [
                    b4_committee_id,
                    b4_committee_name,
                    b4_committee_address,
                    b4_committee_city,
                    b4_committee_state,
                    b4_committee_zip,
                    b4_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4_committee_list) + "\n")
        
     
    with open('formb4a.txt', 'rb') as b4a:
        """
        FormB4A: Donations to independent committees

        Data is added to Entity, Donation
        
        COLUMNS
        =======
        Committee ID|Date Received|Contributor ID|Contribution Date|Cash Contribution|In-Kind Contribution|Unpaid Pledges|Contributor Name
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb4a ..."
        
        b4areader = csvkit.reader(b4a, delimiter = delim)
        b4areader.next()
        
        for row in b4areader:
            b4a_committee_id = row[0]
            b4a_contributor_id = row[2]
            
            if b4a_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4a_committee_id)
                
                #Add committee to Entity
                b4a_committee_name = "" #Committee name
                b4a_committee_address = "" #Address
                b4a_committee_city = "" #City
                b4a_committee_state = "" #State
                b4a_committee_zip = "" #ZIP
                b4a_committee_type = "" #Committee type
                b4a_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b4a_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4a_committee_list = [
                    b4a_committee_id,
                    b4a_committee_name,
                    b4a_committee_address,
                    b4a_committee_city,
                    b4a_committee_state,
                    b4a_committee_zip,
                    b4a_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4a_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4a_committee_list) + "\n")

            if b4a_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4a_contributor_id)
                
                #Add contributor to Entity
                b4a_contributor_name = ' '.join((row[7].strip().upper()).split()).replace('"',"") #Contributor name
                b4a_contributor_address = "" #Address
                b4a_contributor_city = "" #City
                b4a_contributor_state = "" #State
                b4a_contributor_zip = "" #ZIP
                b4a_contributor_type = "" #Contributor type
                b4a_entity_date_of_thing_happening = row[1] #Date used to eval recency on dedupe

                """
                DB fields
                =========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b4a_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4a_contributor_list = [
                    b4a_contributor_id,
                    b4a_contributor_name,
                    b4a_contributor_address,
                    b4a_contributor_city,
                    b4a_contributor_state,
                    b4a_contributor_zip,
                    b4a_contributor_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4a_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4a_contributor_list) + "\n")
                
            #Womp into donations
            if b4a_contributor_id not in SHITCOMMITTEES and b4a_committee_id not in SHITCOMMITTEES:
                #datetest
                b4a_donation_date = row[3]
                b4a_date_test = validDate(b4a_donation_date)
                if b4a_date_test == "broke":
                    b4a_dict = {}
                    b4a_dict["donor_id"] = row[2]
                    b4a_dict["recipient_id"] = row[0]
                    b4a_dict["lookup_name"] = ' '.join((row[7].strip().upper()).split()).replace('"',"")
                    b4a_dict["source_table"] = "b4a"
                    b4a_dict["destination_table"] = "donation"
                    b4a_dict["donation_date"] = b4a_donation_date
                    rows_with_new_bad_dates.append(b4a_dict)
                else:
                    b4a_year = b4a_date_test.split("-")[0]
                    if int(b4a_year) >= 1999:
                        b4a_cash = getFloat(str(row[4])) #cash
                        b4a_inkind_amount = getFloat(str(row[5])) #inkind
                        b4a_pledge_amount = getFloat(str(row[6])) #pledge
                        b4a_inkind_desc = "" #in-kind description
                        
                        """
                        DB fields
                        =========
                        db_id, cash, inkind, pledge, inkind_desc, donation_date, donor_id, recipient_id, donation_year, notes, stance, donor_name
                        """
                        b4a_donation_list = [                        
                            "",
                            b4a_cash,
                            b4a_inkind_amount,
                            b4a_pledge_amount,
                            b4a_inkind_desc,
                            b4a_date_test,
                            b4a_contributor_id,
                            b4a_committee_id,
                            b4a_year,
                            "",
                            "",
                            "",
                        ]
                        donations.write("|".join(b4a_donation_list) + "\n")
      
      
    with open('formb4b1.txt', 'rb') as b4b1:
        """
        FormB4B1: Expenditures by independent committees

        Data is added to Entity, Expenditure, Loan
        
        COLUMNS
        =======
        Form ID Number|Committee ID|Date Received|Committee Expenditure ID|Support/Oppose|Nature of Expenditure|Expenditure Date|Amount|Expense Category|Expenditure Committee Name
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb4b1 ..."
        
        b4b1reader = csvkit.reader(b4b1, delimiter = delim)
        b4b1reader.next()
        
        for row in b4b1reader:
            b4b1_committee_id = row[1]
            b4b1_beneficiary_id = row[3]
            
            if b4b1_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4b1_committee_id)
                
                #Add committee to Entity
                b4b1_committee_name = "" #Committee name
                b4b1_committee_address = "" #Address
                b4b1_committee_city = "" #City
                b4b1_committee_state = "" #State
                b4b1_committee_zip = "" #ZIP
                b4b1_committee_type = "" #Committee type
                b4b1_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business
                
                We're adding b4b1_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4b1_committee_list = [
                    b4b1_committee_id,
                    b4b1_committee_name,
                    b4b1_committee_address,
                    b4b1_committee_city,
                    b4b1_committee_state,
                    b4b1_committee_zip,
                    b4b1_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4b1_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4b1_committee_list) + "\n")
                
            if b4b1_beneficiary_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4b1_beneficiary_id)
                
                #Add beneficiary to Entity
                b4b1_beneficiary_name = ' '.join((row[9].strip().upper()).split()).replace('"',"") #Beneficiary name
                b4b1_beneficiary_address = "" #Address
                b4b1_beneficiary_city = "" #City
                b4b1_beneficiary_state = "" #State
                b4b1_beneficiary_zip = "" #ZIP
                b4b1_beneficiary_type = "" #Beneficiary type
                b4b1_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business
                
                We're adding b4b1_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4b1_beneficiary_list = [
                    b4b1_beneficiary_id,
                    b4b1_beneficiary_name,
                    b4b1_beneficiary_address,
                    b4b1_beneficiary_city,
                    b4b1_beneficiary_state,
                    b4b1_beneficiary_zip,
                    b4b1_beneficiary_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4b1_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4b1_beneficiary_list) + "\n")

            if b4b1_beneficiary_id not in SHITCOMMITTEES and b4b1_committee_id not in SHITCOMMITTEES:
                #datetest
                b4b1_transaction_date = row[6]
                b4b1_date_test = validDate(b4b1_transaction_date)
                if b4b1_date_test == "broke":
                    b4b1_dict = {}
                    b4b1_dict["donor_id"] = row[1]
                    b4b1_dict["recipient_id"] = row[3]
                    b4b1_dict["lookup_name"] = ' '.join((row[9].strip().upper()).split()).replace('"',"")
                    b4b1_dict["source_table"] = "b4b1"
                    b4b1_dict["destination_table"] = "expenditure_or_loan"
                    b4b1_dict["donation_date"] = b4b1_transaction_date
                    rows_with_new_bad_dates.append(b4b1_dict)
                else:
                    b4b1_year = b4b1_date_test.split("-")[0]
                    if int(b4b1_year) >= 1999:
                        b4b1_transaction_type = row[5].upper().strip()
                        
                        #Is it a loan?
                        if b4b1_transaction_type == "L":
                            b4b1_lender_name = ' '.join((row[9].strip().upper()).split()).replace('"',"") #lending committee name
                            b4b1_lender_addr = ""
                            b4b1_loan_amount = row[7]
                            b4b1_loan_repaid = 0.00
                            b4b1_loan_stance = row[4] #0=Support, 1=Oppose
                            b4b1_loan_forgiven = 0.00
                            b4b1_paid_by_third_party = 0.00
                            b4b1_guarantor = ""
                            b4b1_committee_id = row[3] # committee receiving the loan
                            b4b1_lending_committee_id = b4b1_beneficiary_id #lending committee ID
                            
                            """
                            DB fields
                            =========
                            db_id, lender_name, lender_addr, loan_date, loan_amount, loan_repaid, loan_forgiven, paid_by_third_party, guarantor, committee_id, notes, stance, lending_committee_id
                            """
                            b4b1_loan_list = [
                                "", #DB ID
                                b4b1_lender_name, #lender name
                                b4b1_lender_addr, #lender address
                                b4b1_date_test, #loan date
                                str(getFloat(b4b1_loan_amount)), #loan amount
                                str(getFloat(b4b1_loan_repaid)), #amount repaid
                                str(getFloat(b4b1_loan_forgiven)), #amount forgiven
                                str(getFloat(b4b1_paid_by_third_party)), #amount covered by 3rd party
                                b4b1_guarantor, #guarantor
                                b4b1_committee_id, #committee ID
                                "", #notes field
                                b4b1_loan_stance, #stance field
                                b4b1_lending_committee_id, #lending committee ID
                            ]
                            loans.write("|".join(b4b1_loan_list) + "\n")
                        
                        #Is it an expendture?
                        else:
                            b4b1_payee = ' '.join((row[9].strip().upper()).split()).replace('"',"")
                            b4b1_address = ""
                            b4b1_exp_purpose = row[5].strip()
                            b4b1_exp_stance = row[4] #0=Support, 1=Oppose
                            b4b1_committee_id = row[1] #committee ID doing the expenditure
                            
                            #was it an in-kind expenditure?
                            if b4b1_transaction_type.strip().upper() == "I":
                                b4b1_exp_inkind = row[7]
                                b4b1_exp_amount = 0.00
                            else:
                                b4b1_exp_inkind = 0.00
                                b4b1_exp_amount = row[7]
                            
                            """
                            DB fields
                            ==========
                            DB id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                            """
                            b4b1_exp_list = [
                                "",
                                b4b1_payee,
                                b4b1_address,
                                b4b1_date_test,
                                b4b1_exp_purpose,
                                str(getFloat(b4b1_exp_amount)),
                                str(getFloat(b4b1_exp_inkind)),
                                b4b1_committee_id,
                                "",
                                "",
                                b4b1_beneficiary_id,
                                "",
                            ]
                            expenditures.write("|".join(b4b1_exp_list) + "\n")
    
    
    with open('formb4b2.txt', 'rb') as b4b2:
        """
        FormB4B2: Federal and out-of-state disbursements by independent committees

        Data is added to Entity, Expenditure
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|State Code|Total|Expense Category
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb4b2 ..."
        
        b4b2reader = csvkit.reader(b4b2, delimiter = delim)
        b4b2reader.next()
        
        for row in b4b2reader:
            b4b2_committee_id = row[1]
            
            if b4b2_committee_id not in SHITCOMMITTEES:
            #Append ID to master list
                id_master_list.append(b4b2_committee_id)
                
                #Add committee to Entity
                b4b2_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b4b2_committee_address = "" #Address
                b4b2_committee_city = "" #City
                b4b2_committee_state = "" #State
                b4b2_committee_zip = "" #ZIP
                b4b2_committee_type = "" #Committee type
                b4b2_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ==========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b4b2_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                
                b4b2_committee_list = [
                    b4b2_committee_id,
                    b4b2_committee_name,
                    b4b2_committee_address,
                    b4b2_committee_city,
                    b4b2_committee_state,
                    b4b2_committee_zip,
                    b4b2_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4b2_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4b2_committee_list) + "\n")
                
                #date test
                b4b2_transaction_date = row[2]
                b4b2_date_test = validDate(b4b2_transaction_date)
                if b4b2_date_test == "broke":
                    b4b2_dict = {}
                    b4b2_dict["donor_id"] = row[1]
                    b4b2_dict["recipient_id"] = ""
                    b4b2_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b4b2_dict["source_table"] = "b4b2"
                    b4b2_dict["destination_table"] = "expenditure"
                    b4b2_dict["donation_date"] = b4b2_transaction_date
                    rows_with_new_bad_dates.append(b4b2_dict)
                else:
                    b4b2_year = b4b2_date_test.split("-")[0]
                    if int(b4b2_year) >= 1999:
                        #Add to Expenditure
                        b4b2_payee = ""
                        b4b2_address = ""
                        b4b2_purpose = "OUT-OF-STATE DISBURSEMENT"
                        b4b2_amount = row[4]
                        b4b2_inkind = ""
                        
                        """
                        DB fields
                        =========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b4b2_exp_list = [
                            "",
                            b4b2_payee,
                            b4b2_address,
                            b4b2_date_test,
                            b4b2_purpose,
                            b4b2_amount,
                            b4b2_inkind,
                            b4b2_committee_id,
                            "",
                            "",
                            "",
                            "",
                        ]
                        expenditures.write("|".join(b4b2_exp_list) + "\n")
                
                
    with open('formb4b3.txt', 'rb') as b4b3:
        """
        FormB4B3: Administrative expenditures by independent committees

        Data is added to Entity, Expenditure
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|Payee Name|Payee Address|Purpose Of Disbursement|Date of Disbursement|Amount|Expense Category
        
        *** n.b. The column headings in the file include "Report ID", but it doesn't exist in the data ***
        """
        
        print "    formb4b3 ..."
        
        b4b3reader = csvkit.reader(b4b3, delimiter = delim)
        b4b3reader.next()
        
        for row in b4b3reader:
            b4b3_committee_id = row[1]
            
            if b4b3_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b4b3_committee_id)
                
                #Add committee to Entity
                b4b3_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b4b3_committee_address = "" #Address
                b4b3_committee_city = "" #City
                b4b3_committee_state = "" #State
                b4b3_committee_zip = "" #ZIP
                b4b3_committee_type = "" #Committee type
                b4b2_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b4b3_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b4b3_committee_list = [
                    b4b3_committee_id,
                    b4b3_committee_name,
                    b4b3_committee_address,
                    b4b3_committee_city,
                    b4b3_committee_state,
                    b4b3_committee_zip,
                    b4b3_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b4b2_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b4b3_committee_list) + "\n")
        
                #date test
                b4b3_transaction_date = row[6]
                b4b3_date_test = validDate(b4b3_transaction_date)
                if b4b3_date_test == "broke":
                    b4b3_dict = {}
                    b4b3_dict["donor_id"] = row[1]
                    b4b3_dict["recipient_id"] = row[3]
                    b4b3_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b4b3_dict["source_table"] = "b4b3"
                    b4b3_dict["destination_table"] = "expenditure"
                    b4b3_dict["donation_date"] = b4b3_transaction_date
                    rows_with_new_bad_dates.append(b4b3_dict)
                else:
                    b4b3_year = b4b3_date_test.split("-")[0]
                    if int(b4b3_year) >= 1999:
                        #Add to Expenditure
                        b4b3_payee = ' '.join((row[3].strip().upper()).split()).replace('"',"")
                        b4b3_address = ' '.join((row[4].strip().upper()).split()).replace('"',"")
                        b4b3_purpose = ' '.join((row[5].strip().upper()).split()).replace('"',"")
                        b4b3_amount = row[7]
                        b4b3_inkind = ""
                        
                        """
                        DB fields
                        =========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b4b3_exp_list = [
                            "",
                            b4b3_payee,
                            b4b3_address,
                            b4b3_date_test,
                            b4b3_purpose,
                            b4b3_amount,
                            b4b3_inkind,
                            b4b3_committee_id,
                            "",
                            "",
                            "",
                            ""
                        ]
                        expenditures.write("|".join(b4b3_exp_list) + "\n")
       
    
    with open('formb5.txt', 'rb') as b5:
        """
        FormB5: Late donations

        Data is added to Entity, Donation
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Received|Date Last Revised|Last Revised By|Postmark Date|Microfilm Number|Contributor ID|Type of Contributor|Nature of Contribution|Date of Contribution|Amount|Occupation|Employer|Place of Business|Contributor Name
        """
        
        print "    formb5 ..."
        
        b5reader = csvkit.reader(b5, delimiter = delim)
        b5reader.next()
        
        for row in b5reader:
            b5_committee_id = row[1]
            b5_contributor_id = row[7]
            
            if b5_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b5_committee_id)
                
                #Add committee to Entity
                b5_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b5_committee_address = "" #Address
                b5_committee_city = "" #City
                b5_committee_state = "" #State
                b5_committee_zip = "" #ZIP
                b5_committee_type = "" #Committee type
                b5_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b5_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b5_committee_list = [
                    b5_committee_id,
                    b5_committee_name,
                    b5_committee_address,
                    b5_committee_city,
                    b5_committee_state,
                    b5_committee_zip,
                    b5_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b5_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b5_committee_list) + "\n")
        
            if b5_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b5_contributor_id)
                
                #Add contributor to Entity
                b5_contributor_name = ' '.join((row[15].strip().upper()).split()).replace('"',"") #Contributor name
                b5_contributor_address = "" #Address
                b5_contributor_city = "" #City
                b5_contributor_state = "" #State
                b5_contributor_zip = "" #ZIP
                b5_contributor_type = row[8].strip().upper() #Contributor type (B=Business, I=Individual, C=Corporation, M=Candidate committee, P=PAC, Q=Ballot Question Committee, R=Political Party Committee)
                b5_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe
                b5_contributor_occupation = row[12].strip()
                b5_contributor_employer = row[13].strip()
                b5_contributor_place_of_business = row[14].strip()

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b5_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b5_contributor_list = [
                    b5_contributor_id,
                    b5_contributor_name,
                    b5_contributor_address,
                    b5_contributor_city,
                    b5_contributor_state,
                    b5_contributor_zip,
                    b5_contributor_type,
                    "",
                    b5_contributor_employer,
                    b5_contributor_occupation,
                    b5_contributor_place_of_business,
                    "",
                    b5_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b5_contributor_list) + "\n")
       
    
    #now we do the b6 tables with some fly csvjoin ish
    
    """
    FormB6EXPEND: Expenditures on behalf of committees by people or entities who do not have an ID
 
    Data is added to Entity, Expenditure
    
    COLUMNS
    =======
    Committee Name|Form ID Number|Committee ID|Postmark Date|Date Received|Microfilm Number|Expenditure Name|Expend Phone|Expend Address|Expend City|Expend State|Expend Zip|Election Date|Recipient Name|Recipient Address|Expenditure Date|Amount|Description|Date Last Revised|Last Revised By|Committee Name|Form B6 ID|Date Received|Form ID|Expenditure Date|Amount|Description|Recipient Name|Recipient Address
    """
    
    print "    formb6expend ..."
    
    with hide('running', 'stdout', 'stderr'):
        stitched_b6exp = local('csvjoin -d "|" -c "Form ID Number,Form B6 ID" --right formb6.txt formb6expend.txt | csvformat -D "|" |  sed -e \'1d\'', capture=True)
        
        ls = []
        for dude in stitched_b6exp.split("\n"):
            ls.append(dude.split("|"))
        for row in ls:
            b6_committee_id = row[2]
            
            if b6_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b6_committee_id)
                
                #Add committee to Entity
                b6_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b6_committee_address = "" #Address
                b6_committee_city = "" #City
                b6_committee_state = "" #State
                b6_committee_zip = "" #ZIP
                b6_committee_type = "" #Committee type
                b6_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b6_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                
                b6_committee_list = [
                    b6_committee_id,
                    b6_committee_name,
                    b6_committee_address,
                    b6_committee_city,
                    b6_committee_state,
                    b6_committee_zip,
                    b6_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b6_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b6_committee_list) + "\n")
                
                #Womp into Expenditure
                #date test
                b6_transaction_date = row[24]
                b6_date_test = validDate(b6_transaction_date)
                if b6_date_test == "broke":
                    b6_dict = {}
                    b6_dict["donor_id"] = row[6]
                    b6_dict["recipient_id"] = row[2]
                    b6_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b6_dict["source_table"] = "b6expend"
                    b6_dict["destination_table"] = "expenditure"
                    b6_dict["donation_date"] = b6_transaction_date
                    rows_with_new_bad_dates.append(b6_dict)
                    print b6_dict
                else:
                    b6_year = b6_date_test.split("-")[0]
                    if int(b6_year) >= 1999:
                        b6_payee = ' '.join((row[27].strip().upper()).split()).replace('"',"")
                        b6_payee_addr = ' '.join((row[28].strip().upper()).split()).replace('"',"")
                        b6_purpose = ' '.join((row[26].strip().upper()).split()).replace('"',"")
                        b6_amount = row[25]
                        b6_inkind = ""
                        b6_committee_id = ""
                        b6_stance = ""
                        b6_comm_receiving = row[2]
                        b6_exp_name = ' '.join((row[6].strip().upper()).split()).replace('"',"")
                        
                        """
                        DB fields
                        ========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b6_exp_list = [
                            "",
                            b6_payee,
                            b6_payee_addr,
                            b6_date_test,
                            b6_purpose,
                            b6_amount,
                            b6_inkind,
                            b6_committee_id,
                            "",
                            "",
                            b6_comm_receiving,
                            b6_exp_name,
                        ]
                        expenditures.write("|".join(b6_exp_list) + "\n")
    
    
    
    """
    FormB6CONT: Donations to committees by people or entities who do not have an ID
 
    Data is added to Entity, Donation
    
    COLUMNS
    =======
    Committee Name|Form ID Number|Committee ID|Postmark Date|Date Received|Microfilm Number|Expenditure Name|Expend Phone|Expend Address|Expend City|Expend State|Expend Zip|Election Date|Recipient Name|Recipient Address|Expenditure Date|Amount|Description|Date Last Revised|Last Revised By|Committee Name|Form B6 ID|Form ID|Contributor Name|Contributor Address|Occupation|Place Of Business|Employer
    """
    
    print "    formb6cont ..."
    
    with hide('running', 'stdout', 'stderr'):
        stitched_b6don = local('csvjoin -d "|" -c "Form ID Number,Form B6 ID" --right formb6.txt formb6cont.txt | csvformat -D "|" |  sed -e \'1d\'', capture=True)
        
        ls = []
        for dude in stitched_b6don.split("\n"):
            ls.append(dude.split("|"))
        for row in ls:
            b6_don_committee_id = row[2]
            
            if b6_don_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b6_don_committee_id)
                
                #Add committee to Entity
                b6_don_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b6_don_committee_address = "" #Address
                b6_don_committee_city = "" #City
                b6_don_committee_state = "" #State
                b6_don_committee_zip = "" #ZIP
                b6_don_committee_type = "" #Committee type
                b6_don_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b6_don_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                
                b6_don_committee_list = [
                    b6_don_committee_id,
                    b6_don_committee_name,
                    b6_don_committee_address,
                    b6_don_committee_city,
                    b6_don_committee_state,
                    b6_don_committee_zip,
                    b6_don_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b6_don_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b6_don_committee_list) + "\n")
    
                #Womp into donations
                #datetest
                b6_don_donation_date = row[4]
                b6_don_date_test = validDate(b6_don_donation_date)
                if b6_don_date_test == "broke":
                    b6_don_dict = {}
                    b6_don_dict["donor_id"] = row[10]
                    b6_don_dict["recipient_id"] = row[6]
                    b6_don_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b6_don_dict["source_table"] = "b6cont"
                    b6_don_dict["destination_table"] = "donation"
                    b6_don_dict["donation_date"] = b6_don_donation_date
                    rows_with_new_bad_dates.append(b6_don_dict)
                else:
                    b6_don_year = b6_don_date_test.split("-")[0]
                    if int(b6_year) >= 1999:
                        b6_don_cash = str(getFloat(row[16])) #cash
                        b6_don_inkind_amount = "" #inkind
                        b6_don_pledge_amount = "" #pledge
                        b6_don_inkind_desc = "" #in-kind description
                        b6_don_donor_name = ' '.join((row[23].strip().upper()).split()).replace('"',"") #donor name
                        
                        """
                        DB fields
                        ========
                        db_id, cash, inkind, pledge, inkind_desc, donation_date, donor_id, recipient_id, donation_year, notes, stance, donor_name
                        """
                        b6_don_donation_list = [                        
                            "",
                            b6_don_cash,
                            b6_don_inkind_amount,
                            b6_don_pledge_amount,
                            b6_don_inkind_desc,
                            b6_don_date_test,
                            "",
                            b6_don_committee_id,
                            b6_don_year,
                            "",
                            "",
                            b6_don_donor_name,
                        ]
                        donations.write("|".join(b6_don_donation_list) + "\n")
    
    
    with open('formb7.txt', 'rb') as b7:
        """
        FormB7: Registration of corporations, unions and other associations

        Data is added to Entity
        
        COLUMNS
        =======
        Committee Name|Committee ID|Date Last Revised|Last Revised By|Date Received|Postmark Date|Microfilm Number|Type of Contributor|PAC ID|Description Of Services|Report ID|PAC Name
        """
        
        print "    formb7 ..."
        
        b7reader = csvkit.reader(b7, delimiter = delim)
        b7reader.next()
        
        for row in b7reader:
            b7_committee_id = row[1]
            b7_sspf_committee_id = row[8]
            
            if b7_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b7_committee_id)
                
                #Add committee to Entity
                b7_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #Committee name
                b7_committee_address = "" #Address
                b7_committee_city = "" #City
                b7_committee_state = "" #State
                b7_committee_zip = "" #ZIP
                b7_committee_type = row[7].upper().strip() #Committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b7_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b7_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b7_committee_list = [
                    b7_committee_id,
                    b7_committee_name,
                    b7_committee_address,
                    b7_committee_city,
                    b7_committee_state,
                    b7_committee_zip,
                    b7_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b7_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b7_committee_list) + "\n")
            
            if b7_sspf_committee_id.strip() and b7_sspf_committee_id.strip() != "" and b7_sspf_committee_id.strip() not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b7_sspf_committee_id.strip())
                
                #Add sspf committee to Entity
                b7_sspf_committee_name = ' '.join((row[10].strip().upper()).split()).replace('"',"") #Committee name
                b7_sspf_committee_address = "" #Address
                b7_sspf_committee_city = "" #City
                b7_sspf_committee_state = "" #State
                b7_sspf_committee_zip = "" #ZIP
                b7_sspf_committee_descrip = ' '.join((row[9].strip().upper()).split()).replace('"',"")  #description
                b7_sspf_committee_type = row[7].upper().strip() #Committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b7_sspf_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe

                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b7_sspf_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b7_sspf_committee_list = [
                    b7_sspf_committee_id,
                    b7_sspf_committee_name,
                    b7_sspf_committee_address,
                    b7_sspf_committee_city,
                    b7_sspf_committee_state,
                    b7_sspf_committee_zip,
                    b7_sspf_committee_type,
                    b7_sspf_committee_descrip,
                    "",
                    "",
                    "",
                    "",
                    b7_sspf_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b7_sspf_committee_list) + "\n")
                
    
    with open('formb72.txt', 'rb') as b72:
        """
        FormB72: Direct contributions by corporations, unions and other associations

        Data is added to Entity, Donation
        
        COLUMNS
        =======
        Contributor Name|Contributor ID|Date Received|Committee ID|Contribution Date|Amount|Microfilm Number|Committee Name
        
        *** n.b. committee ID/name and contributor ID/name headers are swapped in the raw data , also there is no Report ID, contrary to headers ***
        """
        
        print "    formb72 ..."
        
        b72reader = csvkit.reader(b72, delimiter = delim)
        b72reader.next()
        
        for row in b72reader:
            b72_committee_id = row[3]
            b72_contributor_id = row[1]
            
            if b72_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b72_committee_id)
                
                #Add committee to Entity
                b72_committee_name = ' '.join((row[7].strip().upper()).split()).replace('"',"") #Committee name
                b72_committee_address = "" #Address
                b72_committee_city = "" #City
                b72_committee_state = "" #State
                b72_committee_zip = "" #ZIP
                b72_committee_type = "" #Committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b72_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b72_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b72_committee_list = [
                    b72_committee_id,
                    b72_committee_name,
                    b72_committee_address,
                    b72_committee_city,
                    b72_committee_state,
                    b72_committee_zip,
                    b72_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b72_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b72_committee_list) + "\n")
            
            if b72_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b72_contributor_id)
                
                #Add contributor to Entity
                b72_contributor_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #contributor name
                b72_contributor_address = "" #Address
                b72_contributor_city = "" #City
                b72_contributor_state = "" #State
                b72_contributor_zip = "" #ZIP
                b72_contributor_type = "" #contributor type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b72_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b72_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                b72_contributor_list = [
                    b72_contributor_id,
                    b72_contributor_name,
                    b72_contributor_address,
                    b72_contributor_city,
                    b72_contributor_state,
                    b72_contributor_zip,
                    b72_contributor_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b72_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b72_contributor_list) + "\n")

            #womp into Donation                
            if b72_committee_id not in SHITCOMMITTEES and b72_contributor_id not in SHITCOMMITTEES:
                #datetest
                b72_donation_date = row[4]
                b72_date_test = validDate(b72_donation_date)
                if b72_date_test == "broke":
                    b72_dict = {}
                    b72_dict["donor_id"] = row[1]
                    b72_dict["recipient_id"] = row[3]
                    b72_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b72_dict["source_table"] = "b72"
                    b72_dict["destination_table"] = "donation"
                    b72_dict["donation_date"] = b72_donation_date
                    rows_with_new_bad_dates.append(b72_dict)
                else:
                    b72_year = b72_date_test.split("-")[0]
                    if int(b72_year) >= 1999:
                        b72_cash = getFloat(str(row[5])) #cash                        
                        b72_inkind_amount = "" #inkind
                        b72_pledge_amount = "" #pledge
                        b72_inkind_desc = "" #in-kind description
                        
                        """
                        DB fields
                        ========
                        db_id, cash, inkind, pledge, inkind_desc, donation_date, donor_id, recipient_id, donation_year, notes, stance, donor_name
                        """
                        b72_donation_list = [                        
                            "",
                            b72_cash,
                            b72_inkind_amount,
                            b72_pledge_amount,
                            b72_inkind_desc,
                            b72_date_test,
                            b72_contributor_id,
                            b72_committee_id,
                            b72_year,
                            "",
                            "",
                            " ".join((row[0].strip().upper()).split()).replace('"',""),
                        ]
                        donations.write("|".join(b72_donation_list) + "\n")
    
    
    with open('formb73.txt', 'rb') as b73:
        """
        FormB73: Indirect contributions by corporations, unions and other associations

        Data is added to Entity, Expenditure
        
        COLUMNS
        =======
        Contributor Name|Contributor ID|Date Received|Committee ID|Contribution Date|Amount|Nature Of Contribution|Support/Oppose|Description|Microfilm Number|Committee Name
        
        *** n.b. committee ID/name and contributor ID/name headers are swapped in the raw data, also there is no Report ID, contrary to headers ***
        
        We are grouping "personal service" expenditures with "in-kind"
        
        """
        
        print "    formb73 ..."
        
        b73reader = csvkit.reader(b73, delimiter = delim)
        b73reader.next()
        
        for row in b73reader:
            b73_committee_id = row[3]
            b73_contributor_id = row[1]
            
            if b73_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b73_committee_id)
                
                #Add committee to Entity
                b73_committee_name = ' '.join((row[10].strip().upper()).split()).replace('"',"") #Committee name
                b73_committee_address = "" #Address
                b73_committee_city = "" #City
                b73_committee_state = "" #State
                b73_committee_zip = "" #ZIP
                b73_committee_type = "" #Committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b73_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b73_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b73_committee_list = [
                    b73_committee_id,
                    b73_committee_name,
                    b73_committee_address,
                    b73_committee_city,
                    b73_committee_state,
                    b73_committee_zip,
                    b73_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b73_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b73_committee_list) + "\n")
                
            if b73_contributor_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b73_contributor_id)
                
                #Add contributor to Entity
                b73_contributor_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #contributor name
                b73_contributor_address = "" #Address
                b73_contributor_city = "" #City
                b73_contributor_state = "" #State
                b73_contributor_zip = "" #ZIP
                b73_contributor_type = "" #contributor type (C=Corporation, L=Labor Organization, I=Industry or Trade Association, P=Professional Association)
                b73_entity_date_of_thing_happening = row[2] #Date used to eval recency on dedupe
                 
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b73_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b73_contributor_list = [
                    b73_contributor_id,
                    b73_contributor_name,
                    b73_contributor_address,
                    b73_contributor_city,
                    b73_contributor_state,
                    b73_contributor_zip,
                    b73_contributor_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b73_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b73_contributor_list) + "\n")
            
            if b73_committee_id not in SHITCOMMITTEES and b73_contributor_id not in SHITCOMMITTEES:
                b73_exp_date = row[4]
                b73_exp_date_test = validDate(b73_exp_date)
                if b73_exp_date_test == "broke":
                    b73_dict = {}
                    b73_dict["donor_id"] = ""
                    b73_dict["recipient_id"] = row[3]
                    b73_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b73_dict["source_table"] = "b73"
                    b73_dict["destination_table"] = "expenditures_or_donations"
                    b73_dict["donation_date"] = b73_exp_date
                    rows_with_new_bad_dates.append(b73_dict)
                else:
                    b73_year = b73_exp_date_test.split("-")[0]
                    if int(b73_year) >= 1999:
                        #womp into Expenditure
                        b73_contrib_type = row[6].upper().strip() #(I=In-Kind, P=Personal Service, E=Independent Expenditure)
                        b73_payee = ' '.join((row[10].upper().strip()).split()).replace('"',"")
                        b73_address = ""
                        b73_stance = row[7] #0=support, 1=oppose
                        b73_purpose = ' '.join((row[8].strip().upper()).split()).replace('"',"")
                        b73_contrib_name = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                        
                        if b73_contrib_type == "E":
                            b73_amount = row[5]
                            b73_inkind = ""
                        else:
                            b73_amount = ""
                            b73_inkind = row[5]
                        
                        """
                        DB fields
                        ========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b73_exp_list = [
                            "",
                            b73_payee,
                            b73_address,
                            b73_exp_date_test,
                            b73_purpose,
                            b73_amount,
                            b73_inkind,
                            b73_committee_id,
                            b73_stance,
                            "",
                            b73_contributor_id,
                            b73_contrib_name,
                        ]
                        expenditures.write("|".join(b73_exp_list) + "\n")
    
    
    with open('formb9.txt', 'rb') as b9:
        """
        FormB9: Out of State Contribution/Expenditure Report

        Data is added to Entity
        
        COLUMNS
        =======
        Contributor Name|Form ID|Contributor ID|Postmark Date|Date Received|Microfilm Number|Contributor Type|Date Last Revised|Last Revised By|Contributor Phone
        """
        
        print "    b9 ..."
        
        b9reader = csvkit.reader(b9, delimiter = delim)
        b9reader.next()
         
        for row in b9reader:
            b9_committee_id = row[2]
            
            if b9_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b9_committee_id)
                #Add committee to Entity
                b9_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #committee name
                b9_committee_address = "" #Address
                b9_committee_city = "" #City
                b9_committee_state = "" #State
                b9_committee_zip = "" #ZIP
                b9_committee_type = row[6].upper().strip() #committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Organization, P=Professional Association)
                b9_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b9_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b9_committee_list = [
                    b9_committee_id,
                    b9_committee_name,
                    b9_committee_address,
                    b9_committee_city,
                    b9_committee_state,
                    b9_committee_zip,
                    b9_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b9_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b9_committee_list) + "\n")
        
    
    #use csvjoin on b9b, yo
    
    """
    FormB9B: Out-of-state expenditures, donations, loans

    Data is added to Entity, Expenditure, Donation, Loan
    
    COLUMNS
    =======
    Contributor Name|Form ID|Contributor ID|Postmark Date|Date Received|Microfilm Number|Contributor Type|Date Last Revised|Last Revised By|Contributor Phone|Contributor Name|Form B9 ID|Form ID|Recipient ID|Support/Oppose|Nature of Expenditure|Expenditure Date|Previous Total|Amount|Total|Description|Entry Date|Recipient Name
    """
    
    print "    formb9b ..."
    
    with hide('running', 'stdout', 'stderr'):
        stitched_b9exp = local('csvjoin -d "|" -c "Form ID,Form B9 ID" --right formb9.txt formb9b.txt | csvformat -D "|" |  sed -e \'1d\'', capture=True)
        
        ls = []
        for dude in stitched_b9exp.split("\n"):
            ls.append(dude.split("|"))
        for row in ls:
            b9_exp_committee_id = row[2]
            b9_exp_recipient_id = row[13]
            
            if b9_exp_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b9_exp_committee_id)
                
                #Add committee to Entity
                b9_exp_committee_name = ' '.join((row[10].strip().upper()).split()).replace('"',"") #committee name
                b9_exp_committee_address = "" #Address
                b9_exp_committee_city = "" #City
                b9_exp_committee_state = "" #State
                b9_exp_committee_zip = "" #ZIP
                b9_exp_committee_type = row[6].upper().strip() #committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Organization, P=Professional Association)
                b9_exp_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b9_exp_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                
                b9_exp_committee_list = [
                    b9_exp_committee_id,
                    b9_exp_committee_name,
                    b9_exp_committee_address,
                    b9_exp_committee_state,
                    b9_exp_committee_zip,
                    b9_exp_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b9_exp_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b9_exp_committee_list) + "\n")
                
            if b9_exp_recipient_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b9_exp_recipient_id)
                
                #Add recipient to Entity
                b9_exp_recipient_name = ' '.join((row[22].strip().upper()).split()).replace('"',"") #recipient name
                b9_exp_recipient_address = "" #Address
                b9_exp_recipient_city = "" #City
                b9_exp_recipient_state = "" #State
                b9_exp_recipient_zip = "" #ZIP
                b9_exp_recipient_type = "" #committee type (C=Corporation, L=Labor Organization, I=Industry or Trade Organization, P=Professional Association)
                b9_exp_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b9_exp_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                """
                b9_exp_recipient_list = [
                    b9_exp_recipient_id,
                    b9_exp_recipient_name,
                    b9_exp_recipient_address,
                    b9_exp_recipient_city,
                    b9_exp_recipient_state,
                    b9_exp_recipient_zip,
                    b9_exp_recipient_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b9_exp_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b9_exp_recipient_list) + "\n")
                
            if b9_exp_committee_id not in SHITCOMMITTEES and b9_exp_recipient_id not in SHITCOMMITTEES:
                #datecheck
                b9_exp_date = row[16]
                b9_exp_date_test = validDate(b9_exp_date)
                if b9_exp_date_test == "broke":
                    b9_dict = {}
                    b9_dict["donor_id"] = row[2]
                    b9_dict["recipient_id"] = row[13]
                    b9_dict["lookup_name"] = ' '.join((row[22].strip().upper()).split()).replace('"',"")
                    b9_dict["source_table"] = "b9b"
                    b9_dict["destination_table"] = "expenditures_loans_donations"
                    b9_dict["donation_date"] = b9_exp_date
                    rows_with_new_bad_dates.append(b9_dict)
                else:
                    b9_year = b9_exp_date_test.split("-")[0]
                    if int(b9_year) >= 1999:
                        #what kind is it?
                        b9_contrib_type = row[15].upper().strip() #(A=Direct Contribution, B=In-Kind Contribution, C=Loans, D=Independent Expenditure, E=Pledge)
                        
                        if b9_contrib_type == "L":
                            # do loan shiz here
                            b9_lender_name = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                            b9_lender_addr = ""
                            b9_loan_amount = row[18]
                            b9_loan_repaid = ""
                            b9_loan_forgiven = ""
                            b9_loan_paid_by_third_party = ""
                            b9_loan_guarantor = ""
                            b9_loan_committee_id = row[13]
                            b9_loan_stance = row[14].upper().strip() # (S=Support, O=Oppose)
                            if b9_loan_stance == "S":
                                b9_loan_stance = "0"
                            elif b9_loan_stance == "0":
                                b9_loan_stance = "1"
                            else:
                                b9_loan_stance = ""
                            b9_loan_lending_committee_id = row[2] #lending committee ID
                            
                            """
                            DB fields
                            ========
                            db_id, lender_name, lender_addr, loan_date, loan_amount, loan_repaid, loan_forgiven, paid_by_third_party, guarantor, committee_id, notes, stance, lending_committee_id
                            """
                            b9_loan_list = [
                                "", #DB ID
                                b9_lender_name, #lender name
                                b9_lender_addr, #lender address
                                b9_exp_date_test, #loan date
                                b9_loan_amount, #loan amount
                                b9_loan_repaid, #amount repaid
                                b9_loan_forgiven, #amount forgiven
                                b9_paid_by_third_party, #amount covered by 3rd party
                                b9_guarantor, #guarantor
                                b9_committee_id, #committee ID
                                "", #notes field
                                b9_loan_stance, #stance field
                                b9_loan_lending_committee_id, #lending committee ID
                            ]
                            loans.write("|".join(b9_loan_list) + "\n")
                            
                        elif b9_contrib_type =="D":
                            # do expenditure shiz here
                            b9_exp_payee = ' '.join((row[22].upper().strip()).split()).replace('"',"")
                            b9_exp_address = ""
                            b9_exp_purpose = ' '.join((row[20].strip()).split()).replace('"',"")
                            b9_exp_amount = row[18]
                            b9_exp_inkind = ""
                            b9_exp_receiving_id = row[2]
                            b9_exp_receiving_name = ' '.join((row[0].upper().strip()).split()).replace('"',"")
                            b9_exp_stance = row[14].strip().upper()
                            b9_exp_stance = row[14].upper().strip() # (S=Support, O=Oppose)
                            if b9_exp_stance == "S":
                                b9_exp_stance = "0"
                            elif b9_exp_stance == "0":
                                b9_exp_stance = "1"
                            else:
                                b9_exp_stance = ""
                            
                            """
                            DB fields
                            ========
                            DB id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                            """
                            b9_exp_list = [
                                "",
                                b9_exp_payee,
                                b9_exp_address,
                                b9_exp_date_test,
                                b9_exp_purpose,
                                b9_exp_amount,
                                b9_exp_inkind,
                                b9_committee_id,
                                b9_exp_stance,
                                "",
                                b9_exp_receiving_id,
                                b9_exp_receiving_name,
                            ]
                            expenditures.write("|".join(b9_exp_list) + "\n")
                        else:
                            # do donation shiz here
                            b9_don_contributor_id = row[2]
                            b9_don_receiving_id = row[13]
                            b9_don_contributor_name = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                            b9_don_stance = row[14].upper().strip() # (S=Support, O=Oppose)
                            if b9_don_stance == "S":
                                b9_don_stance = "0"
                            elif b9_don_stance == "0":
                                b9_don_stance = "1"
                            else:
                                b9_don_stance = ""
                            
                            #is it a direct contribution?
                            if b9_contrib_type =="A":
                                b9_don_cash = getFloat(str(row[18]))
                                b9_don_inkind_amount = ""
                                b9_don_pledge_amount = ""
                                b9_don_inkind_desc = ""
                                
                            #is it an in-kind contribution?
                            elif b9_contrib_type == "B":
                                b9_don_inkind_amount = getFloat(str(row[18]))
                                b9_don_cash = ""
                                b9_don_pledge_amount = ""
                                b9_don_inkind_desc = ' '.join((row[20].upper().strip()).split()).replace('"',"")
                                
                            #is it a pledge?
                            elif b9_contrib_type == "E":
                                b9_don_pledge_amount = getFloat(str(row[18]))
                                b9_don_cash = ""
                                b9_don_inkind_amount = ""
                                b9_don_inkind_desc = ""
                            
                            """
                            DB fields
                            ========
                            DB id, cash, inkind, pledge, inkind_desc, donation_date, donor_id, recipient_id, donation_year, notes, stance, donor_name
                            """
                            b9_donation_list = [                        
                                "",
                                b9_don_cash,
                                b9_don_inkind_amount,
                                b9_don_pledge_amount,
                                b9_don_inkind_desc,
                                b9_exp_date_test,
                                b9_don_contributor_id,
                                b9_don_receiving_id,
                                b9_year,
                                "",
                                b9_don_stance,
                                b9_don_contributor_name,
                            ]
                            donations.write("|".join(b9_donation_list) + "\n")

    
    with open('formb11.txt', 'rb') as b11:
        """
        FormB11: Report of Late Independent Expenditure

        Data is added to Entity, Expenditure
        
        COLUMNS
        =======
        Committee Name|Form ID|Committee ID|Postmark Date|Date Received|Microfilm Number|Recipient Name|Recipient Address|Recipient City|Recipient State|Recipient Zip|Recipient Phone|Expenditure Date|Amount|Candidate ID|Candidate Support/Oppose|Ballot Question ID|Ballot Support/Oppose|Date Last Revised|Last Revised By|Candidate/Ballot Name
        """
        
        print "    formb11 ..."
        
        b11reader = csvkit.reader(b11, delimiter = delim)
        b11reader.next()
        
        for row in b11reader:
            b11_committee_id = row[2]
            b11_candidate_id = row[14]
            b11_ballot_id = row[16]
            
            if b11_committee_id not in SHITCOMMITTEES:
                #Append ID to master list
                id_master_list.append(b11_committee_id)
                
                #Add committee to Entity
                b11_committee_name = ' '.join((row[0].strip().upper()).split()).replace('"',"") #committee name
                b11_committee_address = "" #Address
                b11_committee_city = "" #City
                b11_committee_state = "" #State
                b11_committee_zip = "" #ZIP
                b11_committee_type = ""
                b11_entity_date_of_thing_happening = row[4] #Date used to eval recency on dedupe
                
                """
                DB fields
                ========
                nadcid, name, address, city, state, zip, entity_type, notes, employer, occupation, place_of_business, dissolved_date
                
                We're adding b11_entity_date_of_thing_happening so that later we can eval for recency on dedupe.
                
                """
                b11_committee_list = [
                    b11_committee_id,
                    b11_committee_name,
                    b11_committee_address,
                    b11_committee_city,
                    b11_committee_state,
                    b11_committee_zip,
                    b11_committee_type,
                    "",
                    "",
                    "",
                    "",
                    "",
                    b11_entity_date_of_thing_happening,
                ]
                entities.write("|".join(b11_committee_list) + "\n")
                
                # womp expenditures in there
                b11_exp_date = row[12]
                b11_exp_date_test = validDate(b11_exp_date)
                if b11_exp_date_test == "broke":
                    b11_exp_dict = {}
                    b11_exp_dict["donor_id"] = row[2]
                    b11_exp_dict["recipient_id"] = ' '.join((row[6].upper().strip()).split()).replace('"',"")
                    b11_exp_dict["lookup_name"] = ' '.join((row[0].strip().upper()).split()).replace('"',"")
                    b11_exp_dict["source_table"] = "b11"
                    b11_exp_dict["destination_table"] = "expenditures"
                    b11_exp_dict["donation_date"] = b11_exp_date
                    rows_with_new_bad_dates.append(b11_exp_dict)
                else:
                    b11_exp_year = b11_exp_date_test.split("-")[0]
                    if int(b11_exp_year) >= 1999:
                        b11_exp_payee = ' '.join((row[6].upper().strip()).split()).replace('"',"")
                        b11_exp_address = " ".join([row[7], row[8], row[9], row[10]])
                        b11_exp_address = ' '.join((b11_exp_address.upper().strip()).split()).replace('"',"")
                        b11_exp_purpose = ""
                        b11_exp_amount = row[13]
                        b11_exp_inkind = ""
                        b11_exp_beneficiary_name = row[20]
                        
                        if row[14] and row[14] != "" and row[15] and row[15] != "":
                            b11_exp_stance = row[15].upper().strip() # (S=Support, O=Oppose)
                            if b11_exp_stance == "S":
                                b11_exp_stance = "0"
                            elif b11_exp_stance == "0":
                                b11_exp_stance = "1"
                            else:
                                b11_exp_stance = ""
                            b11_exp_beneficiary_id = row[14]
                        else:
                            b11_exp_stance = row[17].upper().strip() # (S=Support, O=Oppose)
                            if b11_exp_stance == "S":
                                b11_exp_stance = "0"
                            elif b11_exp_stance == "0":
                                b11_exp_stance = "1"
                            else:
                                b11_exp_stance = ""
                            b11_exp_beneficiary_id = row[16]
                        
                        """
                        DB fields
                        =========
                        db_id, payee, payee_addr, exp_date, exp_purpose, amount, in_kind, committee_id, stance, notes, committee_receiving_id, comm_name
                        """
                        b11_exp_list = [
                            "",
                            b11_exp_payee,
                            b11_exp_address,
                            b11_exp_date_test,
                            b11_exp_purpose,
                            b11_exp_amount,
                            b11_exp_inkind,
                            b11_committee_id,
                            b11_exp_stance,
                            "",
                            b11_exp_beneficiary_id,
                            b11_exp_beneficiary_name,
                        ]
                        expenditures.write("|".join(b11_exp_list) + "\n")
                
            
    entities.close()
    candidates.close()
    ballotq.close()
    donations.close()
    loans.close()
    expenditures.close()
    
    #check for len() of new bad dates
    if len(rows_with_new_bad_dates) > 0:
        print "\n\nGot some records with bad dates. Go fix this in canonical.py and rerun parser.sh:"
        for thing in rows_with_new_bad_dates:
            print thing
        #local("killall parser.sh", capture=False)
    
    
    """
    Dedupe ballot question file
    =========
    - csvsort ballot-raw.txt by date_we_care_about descending (--reverse)
    - pandas drop_duplicates, keep first record, export
    """
    
    print "\n\nPREPPING BALLOT QUESTION FILE"
    print "    sorting ..."
    
    #sort input file by date
    with hide('running', 'stdout', 'stderr'):
        local('csvsort -d "|" -c 7 --reverse /home/apps/myproject/myproject/nadc/data/toupload/ballot-raw.txt | csvformat -D "|" | sed -e \'s/\"//g\' -e \'s/\&AMP;//g\' > /home/apps/myproject/myproject/nadc/data/toupload/ballot_sorted.txt', capture=False)
    
    print "    deduping ..."
    #dedupe sorted file
    clean_ballot = pd.read_csv("/home/apps/myproject/myproject/nadc/data/toupload/ballot-raw.txt", delimiter="|", dtype={
        "dbid": object,
        "name": object,
        "ballot_type": object,
        "stance": object,
        "nadc_id": object,
        "notes": object,
        "date_we_care_about": object,
        }
    )
    
    deduped_ballot = clean_ballot.drop_duplicates(subset=["name", "nadc_id"])
    deduped_ballot.to_csv('/home/apps/myproject/myproject/nadc/data/toupload/ballot.txt', sep="|", header=False, index=False)

    
    """
    Dedupe entity file
    =========
    - csvsort entity-raw.txt by date_we_care_about
    - loop over unique entity IDs (having taken the set of id_master_list)
    - grep for each ID in the sorted entity file (~1 million times faster than python)
    - loop over the results, compiling a dict with the most recent, non-empty values, if available
    - in the process, kill out variants of "(DISSOLVED)"
    - punch that record into a list
    - write that list to file
    """
    
    print "\n\nPREPPING ENTITY FILE"
    
    #get list of unique entity IDs
    uniques = list(set(id_master_list))
        
    print "   pre-duping ..."
    
    #dedupe sorted file
    clean_entity = pd.read_csv("/home/apps/myproject/myproject/nadc/data/toupload/entity-raw.txt", delimiter="|", dtype={
        "nadcid": object,
        "name": object,
        "address": object,
        "city": object,
        "state": object,
        "zip": object,
        "entity_type": object,
        "notes": object,
        "employer": object,
        "occupation": object,
        "place_of_business": object,
        "dissolved_date": object,
        "date_we_care_about": object,
        }
    )
    
    deduped_entities = clean_entity.drop_duplicates(subset=["nadcid", "name", "address", "city", "state", "zip", "entity_type", "notes", "employer", "occupation", "place_of_business", "dissolved_date"])
    
    deduped_entities.to_csv('/home/apps/myproject/myproject/nadc/data/toupload/entities_deduped.txt', sep="|")
    
    print "   sorting ..."
    
    #sort input file by date
    with hide('running', 'stdout', 'stderr'):
        local('csvsort -d "|" -c 14 /home/apps/myproject/myproject/nadc/data/toupload/entities_deduped.txt | csvformat -D "|" | sed -e \'s/\"//g\' -e \'s/\&AMP;//g\' -e \'1d\' > /home/apps/myproject/myproject/nadc/data/toupload/entities_sorted_and_deduped.txt', capture=False)
    
    #get most current, complete data
    
    #list with variants of "(DISSOLVED)"
    KILLOUT = [
        "(D",
        "(DI",
        "(DIS",
        "(DISS",
        "(DISSO",
        "(DISSOL",
        "(DISSOLV",
        "(DISSOLVE",
        "(DISSOLVED",
        "(DISSOLVED)",
        "(Now-Mccoy For Gov)",
         "- Now Legislature)"
    ]
    
    print "   grepping pre-duped, sorted file and deduping for recency and completeness ..."
    
    entity_final = open("/home/apps/myproject/myproject/nadc/data/toupload/entity.txt", "wb")
    
    for idx, i in enumerate(uniques):
        #print str(idx)
        with hide('running', 'stdout', 'stderr'):
            grepstring = local('grep "' + i + '" /home/apps/myproject/myproject/nadc/data/toupload/entities_sorted_and_deduped.txt', capture=True)
            g = grepstring.split("\n") #list of records that match
            interimdict = {}
            
            #set default values
            interimdict['id'] = ""
            interimdict['canonical_id'] = ""
            interimdict['name'] = ""
            interimdict['canon_name'] = ""
            interimdict['address'] = ""
            interimdict['city'] = ""
            interimdict['state'] = ""
            interimdict['zip'] = ""
            interimdict['entity_type'] = ""
            interimdict['employer'] = ""
            interimdict['occupation'] = ""
            interimdict['place_of_business'] = ""
            interimdict['dissolved_date'] = ""
            
            for dude in g:
                row = dude.split("|") #actual record
                
                nadcid = row[1]
                name = row[2]
                canonical_id = lookItUp(nadcid, "canonicalid", name)
                canonical_name = lookItUp(nadcid, "canonicalname", name)
                
                interimdict['id'] = nadcid
                interimdict['canonical_id'] = canonical_id
                
                #Fix "(DISSOLVED)" ish
                for item in reversed(KILLOUT):
                    name = name.upper().replace(item.upper(), "").strip()
                    canonical_name = canonical_name.upper().replace(item.upper(), "").strip()
                
                #check for complete names
                if len(name) > 1:
                    interimdict['name'] = name
                if len(canonical_name) > 1:
                    interimdict['canon_name'] = canonical_name
                
                #check for complete address
                if len(row[3]) > 1 and len(row[4]) > 1 and len(row[5]) > 1 and len(row[6]) > 1:
                    interimdict['address'] = row[3]
                    interimdict['city'] = row[4]
                    interimdict['state'] = row[5]
                    interimdict['zip'] = row[6]

                #check for complete entity type
                if len(row[7]) >= 1:
                    interimdict['entity_type'] = row[7]

                #check for complete employer
                if len(row[9]) > 1:
                    interimdict['employer'] = row[9]
                    
                #check for complete occupation
                if len(row[10]) > 1:
                    interimdict['occupation'] = row[10]
                    
                #check for complete place of business
                if len(row[11]) > 1:
                    interimdict['place_of_business'] = row[11]
                
                #check for complete dissolved date
                if len(row[12]) > 1:
                    interimdict['dissolved_date'] = row[12]

            #append dict items to list
            outlist = [
                interimdict['id'],
                interimdict['canonical_id'],
                interimdict['name'],
                interimdict['canon_name'],
                interimdict['address'],
                interimdict['city'],
                interimdict['state'],
                interimdict['zip'],
                interimdict['entity_type'],
                "",
                interimdict['employer'],
                interimdict['occupation'],
                interimdict['place_of_business'],
                interimdict['dissolved_date']
            ]
            
            entity_final.write("|".join(outlist) + "\n")
    
    entity_final.close()
    
    
    """
    Dedupe donations file
    =========
    - call pandas drop_duplicates on a subset of fields
    - csvcut the columns we need out of this one
    - chop the header row and kill stray quotes
    """

    print "\n\nPREPPING DONATIONS FILE"
    print "    deduping ..."
    
    clean_donations = pd.read_csv("/home/apps/myproject/myproject/nadc/data/toupload/donations-raw.txt", delimiter="|", dtype={
        "db_id": object,
        "cash": object,
        "inkind": object,
        "pledge": object,
        "inkind_desc": object,
        "donation_date": object,
        "donor_id": object,
        "recipient_id": object,
        "donation_year": object,
        "notes": object,
        "stance": object,
        "donor_name": object
        }
    )
    deduped_donations = clean_donations.drop_duplicates(subset=["donor_id", "donation_date", "recipient_id", "cash", "inkind", "pledge"])
    deduped_donations.to_csv('/home/apps/myproject/myproject/nadc/data/toupload/donations_almost_there.txt', sep="|")
    with hide('running', 'stdout', 'stderr'):
        local('csvcut -x -d "|" -c db_id,cash,inkind,pledge,inkind_desc,donation_date,donor_id,recipient_id,donation_year,notes,stance,donor_name /home/apps/myproject/myproject/nadc/data/toupload/donations_almost_there.txt | csvformat -D "|" | sed -e \'1d\' -e \'s/\"//g\' > /home/apps/myproject/myproject/nadc/data/toupload/donations.txt', capture=False)
    
    print "\n\nDONE."

    
def tweetIt():
    pass
    # Do a thing here to tweet biggest donation in past week
    
    biggest_donation = ""
    string = "New campaign finance data at dataomaha.com/campaign-finance"
    
    
def emailNewShiz():
    pass
    # Do a thing here to email summary tables to interested reporters
