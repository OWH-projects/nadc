#!/bin/bash

#make backup copies of everything
printf "\n~~ christ everyone calm down everything's fine ~~\n\n"
mkdir -p backup
cp *.txt backup
printf "~~ made some backup files ~~\n\n"

#fix date formatting
sed -i 's~\([0-9][0-9]\)/\([0-9][0-9]\)/\([0-9][0-9][0-9][0-9]\)~\3-\1-\2~' *.txt
printf "~~ fixed the date format ~~\n\n"

#truncate existing data
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b1ab;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b2a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b3;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b4a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b5;"
printf "~~ truncated 'em tables ~~\n\n"

#load the cleaned text files into raw mysql tables
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb1ab.txt' INTO TABLE canfin.b1ab FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb2a.txt' INTO TABLE canfin.b2a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb3.txt' INTO TABLE canfin.b3 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb4a.txt' INTO TABLE canfin.b4a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb5.txt' INTO TABLE canfin.b5 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
printf "~~ loaded new data into analysis tables ~~\n\n"

#dedupe getters into toupload/getters.txt
fab dedupeGetters
printf "~~ deduped getters ~~\n\n"

#check for unknown committee IDs, append to toupload/getters.txt
fab whoAintWeKnowAbout
printf "~~ appended stray committees ~~\n\n"

#create mongo file called alldonations.txt
fab stackItUp
printf "~~ created mongo file of donations ~~\n\n"

#dedupe donations from alldonations.txt
fab dedupeDonations
printf "~~ deduped donations ~~\n\n"

# dedupe givers from alldonations.txt
fab dedupeGivers
printf "~~ deduped givers ~~\n\n"

# kill 'n' fill data
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_donation;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_giver;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_getter;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/givers.txt' INTO TABLE django_database.nadc_giver FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/getters.txt' INTO TABLE django_database.nadc_getter FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/donations.txt' INTO TABLE django_database.nadc_donation FIELDS TERMINATED BY '|';"
printf "~~ loaded new data ~~\n\n"
