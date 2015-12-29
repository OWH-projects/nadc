from django import template
register = template.Library()

def returnsearch():
    str = '<h3 class="bold">Search</h3><form id="entity" action="/campaign-finance/search" method="GET"><div class="input-group"><input type="text" class="form-control input-sm" name="q" value="" placeholder="Campaign, donor or PAC"><span class="input-group-btn"><button class="btn btn-primary btn-sm" type="submit">Search</button></span></div></form>'    
    return str

register.simple_tag(returnsearch)