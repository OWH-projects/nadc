#Nebraska campaign finance data

<img src="https://media.giphy.com/media/z9BW7ApDO6hTq/giphy.gif" style="width:100%;" />

A Django app to display political contribution data from the Nebraska Accountability and Disclosure Commission. Go <a href="https://github.com/OWH-projects/nadc_data">here</a> if you're looking for the scripts that download, parse and load the raw data.

##App overview
###Models
<ul>
<li><code>Entity</code>: Any group, committee, donor, lender or other entity that has been assigned a unique ID by the NADC. This is the parent table.</li>
<li><code>Donation</code>: Money, in-kind donations, "direct expenditures" to a committee, pledges.</li>
<li><code>Candidate</code>: Candidates tied to campaign committees and ballot questions.</li>
<li><code>Loans</code></li>
<li><code>Expenditure</code>: Includes both administrative expenses and "targeted" expenses that were earmarked to support or oppose a candidate or committee.</li>
</ul>
