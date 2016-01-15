import datetime
from django import template
from myproject.nadc.models import *

register = template.Library()

@register.inclusion_tag('nadc/additionalinfo.html')
def additionalinfo(id):
    
    #If the entity's canonical ID exists in the AdditionalInfo table, return that record. If the AdditionalInfo record has a candidate ID, return a filtered set of Candidate records, too.
    if AdditionalInfo.objects.filter(canonical=id).count() > 0:
        extrainfo = AdditionalInfo.objects.get(canonical=id)
        if extrainfo.candidate:
            candidates = Candidate.objects.filter(cand_id=extrainfo.candidate)
        else:
            candidates = ""
     
    #If the entity's ID if for a committee that has a relationship to a candidate, return the AdditionalInfo record.
    elif Candidate.objects.filter(committee=id).values('cand_id').count() > 0:
        cand = Candidate.objects.filter(committee=id)
        if len(cand) > 0:
            candidate_id = cand[0].cand_id
            try:
                extrainfo = AdditionalInfo.objects.get(candidate=candidate_id)
                candidates = Candidate.objects.filter(cand_id=candidate_id)
            except:
                extrainfo = ""
                candidates = ""
        else:
            extrainfo = ""
            candidates = ""
            
    elif AdditionalInfo.objects.filter(associated__nadcid=id).count() > 0:
        extrainfo = AdditionalInfo.objects.get(associated__nadcid=id)
        if extrainfo.candidate:
            candidates = Candidate.objects.filter(cand_id=extrainfo.candidate)
        else:
            candidates = ""
            
    
    
    #Otherwise, return nothing.
    else:
        extrainfo = ""
        candidates = ""

    return {'extrainfo':extrainfo, 'candidates':candidates,}