#Nebraska campaign finance data

<img src="https://media.giphy.com/media/z9BW7ApDO6hTq/giphy.gif" style="width:100%;" />

A Django app to display political contribution data from the Nebraska Accountability and Disclosure Commission. The scripts that download and parse the raw data live <a href="https://github.com/OWH-projects/nadc_data">here</a>.

##App overview
###Models
<ul>
<li><code>Entity</code>: Any group, committee, donor, lender or other entity that has been assigned a unique ID by the NADC. This is the parent table.</li>
<li><code>Ballot</code>: Ballot question committees.</li>
<li><code>Donation</code>: Money, in-kind donations, "direct expenditures" to a committee, pledges.</li>
<li><code>Candidate</code>: Candidates tied to campaign committees.</li>
<li><code>Loan</code>: Loans.</li>
<li><code>Expenditure</code>: Both administrative and independent.</li>
</ul>
