#Nebraska campaign finance data

<img src="https://media.giphy.com/media/z9BW7ApDO6hTq/giphy.gif" style="width:100%; max-width:100%;" />

A Django app to import, standardize and display political contribution data from the Nebraska Accountability and Disclosure Commission. Run `pip install -r requirements.txt` to install the dependencies:
- [csvkit](https://csvkit.readthedocs.org/en/0.9.1/)  
- [pandas!](http://pandas.pydata.org/pandas-docs/stable/)  
- [fabric](http://www.fabfile.org/)

We expect to get regular data dumps from the NADC and overwrite the database in full. The update process:
<ol>
<li>Drop new data files into <code>nadc/data</code>.</li>
<li>Run <code>nadc/data/parser.sh</code></li>
<li>If there are new, invalid dates that we haven't encountered in the past, you'll be prompted to add those to a dict in <code>nadc/data/canonical/canonical.py</code></li>
</ol>

##Overview
A standard data dump from the NADC yields 61 pipe-delimited text files (data dictionary at: `nadc/data/nadc_tables.rtf`). We focus on eight of them:
<ul>
<li><strong>Form A1</strong>: Lookup table for campaign committees</li>
<li><strong>Form A1CAND</strong>: Candidates tied to campaign committees</li>
<li><strong>Form B1AB</strong>: Main table of individual/other contributions</li>
<li><strong>Form B1C</strong>: Loans to campaign committees</li>
<li><strong>Form B1D</strong>: Expenditures by campaign committees</li>
<li><strong>Form B2A</strong>: Contributions to political party committees</li>
<li><strong>Form B4A</strong>: PAC contributions</li>
<li><strong>Form B5</strong>: Late contributions</li>
</ul>

A shell script, `nadc/data/parser.sh`, makes backups of the raw data, loads a MySQL database with raw data for separate analysis and boils down these eight files (which contain duplicate donations, recipients and donors between tables) into six tables of unique(ish, we'll get to that) entities:
<ul>
<li><code>nadc/data/toupload/getters.txt</code>: Any group or individual who received a donation. These come exclusively from Form A1.</li>
<li><code>nadc/data/toupload/givers.txt</code>: Any group or individual who gave a donation to a Getter. Could come from B1AB, B2A, B4A or B5. (Some donations are duplicated among those tables.)</li>
<li><code>nadc/data/toupload/donations.txt</code>: Money, inkind donations or pledges to getters from givers.</li>
<li><code>nadc/data/toupload/candidates.txt</code>: Candidates tied to campaign committees.</li>
<li><code>nadc/data/toupload/loans.txt</code>: Lending to campaign committees.</li>
<li><code>nadc/data/toupload/expenditures.txt</code>: Expenditures by campaign committees.</li>
</ul>

The clean files are then uploaded to the MySQL database that powers our Django app. For now, database credentials are stored as environmental variables. Maybe this should be changed.

##Handling duplication
###Names
NADC has unique identifiers for each donor, but they identify only the address and exact name. If "Matt Wynn" at 1314 Douglas St. gave money, and "Matthew A Wynn" at 1300 Douglas St. gave money, they're considered two different donors.

This is wrong.

Our solution was to create a lookup dict (`nadc/data/canonical/canonical.py`) for any "large" donors, whether in terms of total donations or the number of donations. Super fellow [Daniel Wheaton](https://twitter.com/theheroofthyme) assigned new, real unique identifiers for any of the top 100 donors by both measures. Those lists overlapped a bit, so we wound up deduplicating around 70 givers on the first pass. This is why each giver has two ids, with canonical_id representing our assignment of an identity.

The NADC ID is copied to canonical_id for records that are not deduplicated. Getter records were basically clean and didn't require the same methods.

###Donations
Some donations are recorded in several places. A late donation, for instance, may also show up as a normal donation record in B1AB.

Donations can also be duplicated within a record, inaccurately. For example, a 1999 ballot committee reported each of its donations twice, leading to a vastly inflated fundraising report.

Susan Lorenz at the Nebraska Accountability and Disclosure Commission told us that donations from a giver to an orgnization on the same day should not be duplicated. Therefore, we deduplicated using those three values.

##Known problems
###Dates
Very few records have data entry problems with dates. We added these to a lookup dict in `nadc/data/canonical/canonical.py` and they get fixed on import.

Since we can't predict the ways dates will be screwed up in the future, we halt `nadc/data/parser.sh` when confronted with an invalid date that doesn't exist in the lookup.

###Purposeful duplication
Somehow, about a dozen organizations in Form A1 show up multiple times. We handle these with pandas' [`drop_duplicates`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.drop_duplicates.html).

###Donor types
Donors to independent expenditure committees and political party committees don't have a "type" (individual, corporate, etc.) listed. Nearly every one of these donors show up in another table, however, so we extract type data from other tables to round out these records.

##Data excluded
<ul>
<li>Pre-1999 records, which the NADC does not consider especially reliable.</li>
<li>Loans from the handful of committees that didn't receive any reportable donations.</li>
<li>Loans and expenditures with invalid dates.</li>
<li>Any candidates, loans or expenditures attached to a committee that doesn't appear in the NADC's lookup table(s).</li>
</ul>
