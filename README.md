```
                   .___      
  ____ _____     __| _/____  
 /    \\__  \   / __ |/ ___\ 
|   |  \/ __ \_/ /_/ \  \___ 
|___|  (____  /\____ |\___  >
     \/     \/      \/    \/ 

```

An app to import, standardize and display political contribution data from the Nebraska Accountability and Disclosure Commission.

Dependencies: 
- [csvkit](https://csvkit.readthedocs.org/en/0.9.1/)  
- [pandas!](http://pandas.pydata.org/pandas-docs/stable/)  
- [fabric](http://www.fabfile.org/)  

We expect to get a full dump from the NADC every year and overwrite the database in full. The update process is
<ol>
<li>Drop new data files into nadc/data.</li>
<li>Run parser.sh</li>
<li>If there are new incorrect dates that we haven't encountered, you'll be prompted to add those to canonical/canonical.py</li>
</ol>

##Overview
A standard data dump from the NADC yields 61 pipe-delimited text files (data dictionary at: `/data/nadc_tables.rtf`). We focus on five:
<ul>
<li>Form A1: Lookup table for committees</li>
<li>Form B1AB: Main table of individual/other contributions</li>
<li>Form B2A: Contributions to political party committees</li>
<li>Form B4A: PAC contributions</li>
<li>Form B5: Late contributions</li>
</ul>

A fabfile boils our five tables (which contain duplicate donations, recipients and donors between tables) into three tables of unique(ish, we'll get to that) entities:
<ul>
<li>Getters: Any group or individual who received a donation. These come exclusively from Form A1.</li>
<li>Givers: Any group or individual who gave a donation to a Getter. Could come from B1AB, B2A, B4A or B5. Further, the same donation could be duplicated among those tables.</li>
<li>Donations: Money, inkind donations or pledges to getters from givers. </li>
</ul>

##Handling duplication
###Names
NADC has unique identifiers for each donor, but they identify only address and exact name. If "Matt Wynn" at 1314 Douglas St gave, and "Matthew A Wynn" at 1300 Douglas Street gave, they would be considered two different donors.
This is wrong.
Our solution was to create a lookup for any "large" donors, whether in terms of total donations or the number of donations. Super fellow [Daniel Wheaton] (https://twitter.com/theheroofthyme) assigned new, real unique identifiers for any of the top 100 donors by both measures. Those lists overlapped a bit, so we wound up dedupklicating around 70 givers all told. This is why Givers have two ids, with canonical_id representing our assignment of an identity.
The NADC is is copied to canonical_id for records that are not deduplicated.
Getter records were clean and did not require the same method.

###Donations
Some donations are recorded in several places. A late donation, for instance, may also show up as a normal record in B1AB.
Donations can also be duplicated within a record, inaccurately. For example, a 1999 ballot committee reported each of its donations twice, leading to a vastly inflated fundraising report. 
Susan Lorenz at the Nebraska Accountability and Disclosure Commission told us that donations from a giver to an orgnization on the same day should nto be duplicated. Therefore, we deduplicated using those three values.

##Known problems
###Dates
Very few records have data entry problems with dates. We added these to a dictionary in canonical and they are fixed on import.
Since we can't predict the ways dates will be screwed up in the future, we halt import on dates that don't exist yet aren't in canonical.

###Purposeful duplication
Somehow, about a dozen organizations in Form A1 show up multiple times. We handle these with pandas deduplication.





