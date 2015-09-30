from django import template
register = template.Library()

def returnsearch():
    str = '<div class="well"><h3 style="margin-top:0;"><i class="fa fa-search"></i> Search</h3><p>Find a campaign, donor or PAC.</p><form action="/campaign-finance/search" method="GET"><input type="search" class="form-control input-lg" name="q" value="" placeholder="Search ..."></form></div>'    
    return str

register.simple_tag(returnsearch)