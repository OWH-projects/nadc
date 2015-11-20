#Nebraska campaign finance data

<img src="https://media.giphy.com/media/z9BW7ApDO6hTq/giphy.gif" style="width:100%; max-width:100%;" />

A Django app to import, standardize and display political contribution data from the Nebraska Accountability and Disclosure Commission. Run `pip install -r requirements.txt` to install the dependencies:
- [csvkit](https://csvkit.readthedocs.org/en/0.9.1/)  
- [pandas!](http://pandas.pydata.org/pandas-docs/stable/)  
- [fabric](http://www.fabfile.org/)

The NADC now offers weekly updates of campaign finance data. Our script, which takes ~6 minutes to run, fetches new data, parses it and overwrites the database in full. The update process:
<ol>
<li>Run <code>nadc/data/parser.sh</code></li>
<li>If there are new, invalid dates that we haven't encountered in the past, you'll be prompted to add those to a dict in <code>nadc/data/canonical/canonical.py</code></li>
</ol>

##Overview
A standard data dump from the NADC yields 61 pipe-delimited text files (data dictionary at: `nadc/data/nadc_tables.rtf`). We extract data from 24 of them:
<ul>
<li><strong>Form A1</strong>: Lookup table for most committees</li>
<li><strong>Form A1CAND</strong>: Candidates tied to campaign committees</li>
<li><strong>Form B1</strong>: Campaign statements for candidate or ballot question committees</li>

<li><strong>Form B1AB</strong>: Main table of individual/other contributions</li>
<li><strong>Form B1C</strong>: Loans to campaign committees</li>
<li><strong>Form B1D</strong>: Expenditures by campaign committees</li>
<li><strong>Form B2</strong>: Campaign statements for political party committees</li>
<li><strong>Form B2A</strong>: Contributions to political party committees</li>
<li><strong>Form B2B</strong>: Expenditures by political party committees</li>
<li><strong>Form B4</strong>: Campaign statements for independent committees</li>
<li><strong>Form B4A</strong>: Contributions to independent committees</li>
<li><strong>Form B4B1</strong>: Expenditures by independent committees</li>
<li><strong>Form B4B2</strong>: Federal and out-of-state disbursements</li>
<li><strong>Form B4B3</strong>: Administrative/operating disbursements</li>
<li><strong>Form B5</strong>: Late contributions</li>
<li><strong>Form B6</strong>: Reports of an independent expenditure or donation made by people or entities that are not registered as committees</li>
<li><strong>Form B6EXPEND</strong>: Expenditures made on behalf of committees by people who do not have an ID</li>
<li><strong>Form B7</strong>: Registration of corporations, unions and other associations</li>
<li><strong>Form B72</strong>: Donations by corporations, unions and other associations</li>
<li><strong>Form B73</strong>: Indirect contributions by corporations, unions and other associations</li>
<li><strong>Form B9</strong>: Out of state expenditures/donations</li>
<li><strong>Form B9B</strong>: Out of state expenditures</li>
<li><strong>Form B11</strong>: Report of late independent expenditure</li>
</ul>

A shell script, `nadc/data/parser.sh`, makes backups of the raw data and boils down these 24 files (which contain some duplicate transactions) into six data tables:
<ul>
<li><code>nadc/data/toupload/entity.txt</code>: Any group, committee, donor, lender or other entity that has been assigned a unique ID by the NADC. This is the parent table.</li>
<li><code>nadc/data/toupload/ballot.txt</code>: Ballot question committees.</li>
<li><code>nadc/data/toupload/donations.txt</code>: Money, inkind donations and pledges.</li>
<li><code>nadc/data/toupload/candidates.txt</code>: Candidates tied to campaign committees.</li>
<li><code>nadc/data/toupload/loans.txt</code>: Lending.</li>
<li><code>nadc/data/toupload/expenditures.txt</code>: Expenditures.</li>
</ul>

The clean files are then uploaded to the MySQL database that powers our Django app. Database credentials are stored as environmental variables.

##Handling duplication
###Names
NADC has unique identifiers for each donor, but they identify only the address and exact name. If "Matt Wynn" at 1314 Douglas St. gave money, and "Matthew A Wynn" at 1300 Douglas St. gave money, they're considered two different donors.

This is wrong.

We can't deduplicate every donor, so our solution was to create a lookup dictionary (`nadc/data/canonical/canonical.py`) for any "large" donors, whether in terms of total donations or the number of donations. Super fellow [Daniel Wheaton](https://twitter.com/theheroofthyme) assigned new, real unique identifiers for any of the top 100 donors by both measures. Those lists overlapped a bit, so we wound up deduplicating around 70 donors on the first pass. This is why each entity has two ids, with canonical_id representing our assignment of an identity.

The NADC ID is copied to canonical_id for records that are not deduplicated; same with the name.

###Donations
Some donations are recorded in several places. A late donation, for instance, may also show up as a normal donation record in B1AB.

Donations can also be duplicated within a table, inaccurately. For example, a 1999 ballot committee reported each of its donations twice, leading to a vastly inflated fundraising report.

Susan Lorenz at the Nebraska Accountability and Disclosure Commission told us that donations from a giver to an organization on the same day should not be duplicated. Therefore, we deduplicated using those three values.

##Known problems
###Dates
Some records have invalid dates. Others have placeholders (9999-99-99, 1900-01-01, etc.). We added these to a python dictionary in `nadc/data/canonical/canonical.py` and they get fixed on import.

We can't predict the ways dates will be screwed up in the future, so we halt `nadc/data/parser.sh` when confronted with an invalid date that doesn't already exist in our lookup.

###Purposeful duplication
To get an exhaustive list of ID'd entities, the script slurps up a half-million records and reduces them to a file about a tenth that size. We use pandas' [`drop_duplicates`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.drop_duplicates.html) function, grep and python to ensure to return a set of deduplicated records with the most recent, comprehensive data.

##Data excluded
<ul>
<li>Pre-1999 records, which the NADC does not consider especially reliable.</li>
<li>The "more detailed" expenditure information in the handful of records in <code>Form B6CONT</code>. It is a garbage fire.</li>
</ul>