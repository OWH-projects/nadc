#!/bin/bash

#make backup copies of everything
echo "christ everyone calm down everything's fine"
mkdir -p backup
cp *.txt backup
echo "Made some backup files."

#fix date formatting
sed -i 's~\([0-9][0-9]\)/\([0-9][0-9]\)/\([0-9][0-9][0-9][0-9]\)~\3-\1-\2~' *.txt
echo "Fixed the date format."

#truncate existing data
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b1ab;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b2a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b3;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b4a;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "TRUNCATE canfin.b5;"
echo "Truncated 'em tables."

#load the cleaned text files into raw mysql tables
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb1ab.txt' INTO TABLE canfin.b1ab FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb2a.txt' INTO TABLE canfin.b2a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb3.txt' INTO TABLE canfin.b3 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb4a.txt' INTO TABLE canfin.b4a FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
mysql --local-infile -u ${FUSSY_USER} -p${FUSSY_PW} -e "LOAD DATA LOCAL INFILE 'formb5.txt' INTO TABLE canfin.b5 FIELDS TERMINATED BY '|' IGNORE 1 LINES;"
echo "Loaded new data."

#fab makeTables

#fab loadData
