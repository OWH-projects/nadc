#!/bin/bash

#fetch the files, yo
printf "\n~~ fetching new data ~~\n"
cd /home/apps/myproject/myproject/nadc/data
wget http://www.nebraska.gov/nadc_data/nadc_data.zip
unzip -j nadc_data.zip
rm nadc_data.zip
printf "~~ fetched 'at data ~~\n\n"

#parse the "last updated" date
printf "\n~~ parsing \"last updated\" date ~~\n"
fab parseDate
printf "~~ parsed \"last updated\" date ~~\n\n"

#make backup copies of everything
printf "\n~~ making some backup files ~~\n"
mkdir -p /home/apps/myproject/myproject/nadc/data/backup
cp *.txt /home/apps/myproject/myproject/nadc/data/backup
printf "~~ made some backup files ~~\n\n"

#fix date formatting
printf "~~ fixing the date format ~~\n"
sed -i 's~\([0-9][0-9]\)/\([0-9][0-9]\)/\([0-9][0-9][0-9][0-9]\)~\3-\1-\2~' *.txt
printf "~~ fixed the date format ~~\n\n"

#main script that parses raw data into tables for upload
printf "~~ doing all the things ~~\n"
fab parseErrything
printf "~~ did all the things ~~\n\n"

#pick up after yourself
printf "~~ cleaning up ~~\n"
rm /home/apps/myproject/myproject/nadc/data/toupload/donations-raw.txt
rm /home/apps/myproject/myproject/nadc/data/toupload/entities-raw.txt
printf "~~ cleaned up ~~\n\n"

# kill 'n' fill data
printf "~~ killing and filling new data ~~\n"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_donation;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_candidate;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_loan;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE django_database.nadc_expenditure;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_entity;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "DELETE FROM django_database.nadc_ballot;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/entities.txt' INTO TABLE django_database.nadc_entity FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/donations.txt' INTO TABLE django_database.nadc_donation FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/candidates.txt' INTO TABLE django_database.nadc_candidate FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/loans.txt' INTO TABLE django_database.nadc_loan FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/expenditures.txt' INTO TABLE django_database.nadc_expenditure FIELDS TERMINATED BY '|';"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE '/home/apps/myproject/myproject/nadc/data/toupload/ballotq.txt' INTO TABLE django_database.nadc_ballot FIELDS TERMINATED BY '|';"
printf "~~ killed and filled new data ~~\n\n"

printf "~~ DONE ~~"