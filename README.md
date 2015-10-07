```
                                               .___      
                              ____ _____     __| _/____  
                             /    \\__  \   / __ |/ ___\ 
                            |   |  \/ __ \_/ /_/ \  \___ 
                            |___|  (____  /\____ |\___  >
                                 \/     \/      \/    \/ 

```

An app to import, standardize and display political contribution data from the Nebraska Accountability and Disclosure Commission.



<img src="https://media.giphy.com/media/YU0HoCQidyGEE/giphy.gif" style="max-width:100%;" />

Dependencies: 
- [csvkit](https://csvkit.readthedocs.org/en/0.9.1/)  
- [pandas!](http://pandas.pydata.org/pandas-docs/stable/)  
- [fabric](http://www.fabfile.org/)  

So: `pip install -r requirements.txt`

We expect to get a full dump from the NADC every year and overwrite the database in full. The update process is
<ol>
<li>Drop new data files into nadc/data.</li>
<li>Run <code>parser.sh</code></li>
<li>If there are new, invalid dates that we haven't encountered in the past, you'll be prompted to add those to <code>data/canonical/canonical.py</code></li>
</ol>

##Overview
A standard data dump from the NADC yields 61 pipe-delimited text files (data dictionary at: `data/nadc_tables.rtf`). We focus on eight of them:
<ul>
<li>Form A1: Lookup table for campaign committees</li>
<li>Form A1CAND: Candidates tied to campaign committees</li>
<li>Form B1AB: Main table of individual/other contributions</li>
<li>Form B1C: Loans to campaign committees</li>
<li>Form B1D: Expenditures by campaign committees</li>
<li>Form B2A: Contributions to political party committees</li>
<li>Form B4A: PAC contributions</li>
<li>Form B5: Late contributions</li>
</ul>

A shell script, `data/parser.sh`, makes backups of the raw data, loads a mysql database with raw data from a couple key tables for separate analysis and boils down these eight files (which contain duplicate donations, recipients and donors between tables) into six tables of unique(ish, we'll get to that) entities:
<ul>
<li><code>toupload/getters.txt</code>: Any group or individual who received a donation. These come exclusively from Form A1.</li>
<li><code>toupload/givers.txt</code>: Any group or individual who gave a donation to a Getter. Could come from B1AB, B2A, B4A or B5. (Some donations are duplicated among those tables.)</li>
<li><code>toupload/donations.txt</code>: Money, inkind donations or pledges to getters from givers.</li>
<li><code>toupload/candidates.txt</code>: Candidates tied to campaign committees.</li>
<li><code>toupload/loans.txt</code>: Lending to campaign committees.</li>
<li><code>toupload/expenditures.txt</code>: Expenditures by campaign committees.</li>
</ul>

The clean files are then uploaded to the Django MySQL database that powers the app.

##Handling duplication
###Names
NADC has unique identifiers for each donor, but they identify only the address and exact name. If "Matt Wynn" at 1314 Douglas St. gave money, and "Matthew A Wynn" at 1300 Douglas St. gave money, they're considered two different donors.

This is wrong.

Our solution was to create a lookup dict (`canonical/canonical.py`) for any "large" donors, whether in terms of total donations or the number of donations. Super fellow [Daniel Wheaton](https://twitter.com/theheroofthyme) assigned new, real unique identifiers for any of the top 100 donors by both measures. Those lists overlapped a bit, so we wound up deduplicating around 70 givers on the first pass. This is why each giver has two ids, with canonical_id representing our assignment of an identity.

The NADC ID is copied to canonical_id for records that are not deduplicated. Getter records were basically clean and didn't require the same methods.

###Donations
Some donations are recorded in several places. A late donation, for instance, may also show up as a normal donation record in B1AB.

Donations can also be duplicated within a record, inaccurately. For example, a 1999 ballot committee reported each of its donations twice, leading to a vastly inflated fundraising report.

Susan Lorenz at the Nebraska Accountability and Disclosure Commission told us that donations from a giver to an orgnization on the same day should not be duplicated. Therefore, we deduplicated using those three values.

##Known problems
###Dates
Very few records have data entry problems with dates. We added these to a lookup dict in `canonical/canonical.py` and they get fixed on import.

Since we can't predict the ways dates will be screwed up in the future, we halt `parser.sh` when confronted with an invalid date that doesn't exist in the lookup.

###Purposeful duplication
Somehow, about a dozen organizations in Form A1 show up multiple times. We handle these with pandas' [`drop_duplicates`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.drop_duplicates.html).

##Data excluded
<ul>
<li>Pre-1999 records, which are not considered reliable.</li>
<li>Loans from the handful of committees that didn't receive any reportable donations.</li>
<li>Loans and expenditures that had invalid dates.</li>
<li>Candidates or expenditures attached to a committee that doesn't appear in the NADC's lookup table(s).</li>
</ul>