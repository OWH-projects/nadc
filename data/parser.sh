#!/bin/bash

#make backup copies of everything
printf "\n~~ making some backup files ~~\n"
mkdir -p backup
cp *.txt backup
printf "~~ made some backup files ~~\n\n"

#fix date formatting
printf "~~ fixing the date format ~~\n"
sed -i 's~\([0-9][0-9]\)/\([0-9][0-9]\)/\([0-9][0-9][0-9][0-9]\)~\3-\1-\2~' *.txt
printf "~~ fixed the date format ~~\n\n"

#truncate existing data
printf "~~ truncating raw analysis tables ~~\n"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b1ab;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b2a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b3;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b4a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b5;"
printf "~~ truncated raw analysis tables ~~\n\n"

#load the cleaned text files into raw mysql tables
printf "~~ loading new data into analysis tables ~~\n"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb1ab.txt' INTO TABLE canfin.b1ab FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb2a.txt' INTO TABLE canfin.b2a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb3.txt' INTO TABLE canfin.b3 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb4a.txt' INTO TABLE canfin.b4a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb5.txt' INTO TABLE canfin.b5 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
printf "~~ loaded new data into analysis tables ~~\n\n"

#dedupe getters into toupload/getters.txt
printf "~~ deduping getters ~~\n"
fab dedupeGetters
printf "~~ deduped getters ~~\n\n"

#check for unknown committee IDs, append to toupload/getters.txt
printf "~~ appending stray committee IDs ~~\n"
fab whoAintWeKnowAbout
printf "~~ appended stray committee IDs ~~\n\n"

#parse loan data
printf "~~ parsing loan data ~~\n"
fab parseLoans
printf "~~ parsed loan data ~~\n\n"

#parse candidate data
printf "~~ parsing candidate data ~~\n"
fab parseCands
printf "~~ parsed candidate data ~~\n\n"

#create mongo file called alldonations.txt
printf "~~ creating mongo file of donations ~~\n"
fab stackItUp
printf "~~ created mongo file of donations ~~\n\n"

#dedupe donations from alldonations.txt
printf "~~ deduping donations ~~\n"
fab dedupeDonations
printf "~~ deduped donations ~~\n\n"

# dedupe givers from alldonations.txt
printf "~~ deduping givers ~~\n"
fab dedupeGivers
printf "~~ deduped givers ~~\n\n"

# kill 'n' fill data
printf "~~ killing and filling new data ~~\n"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_donation;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_candidate;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_giver;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_getter;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/givers.txt' INTO TABLE django_database.nadc_giver FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/getters.txt' INTO TABLE django_database.nadc_getter FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/donations.txt' INTO TABLE django_database.nadc_donation FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/candidates.txt' INTO TABLE django_database.nadc_candidate FIELDS TERMINATED BY '|';"
printf "~~ killed and filled new data ~~\n\n"

#cleanup
printf "~~ cleaning up ~~\n"
rm /home/apps/myproject/myproject/nadc/data/deduped.csv /home/apps/myproject/myproject/nadc/data/alldonations.txt /home/apps/myproject/myproject/nadc/data/rawgivers.txt
printf "~~ cleaned up ~~\n\n"

printf "~~ DONE. ~~"