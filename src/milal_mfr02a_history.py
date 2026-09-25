"""Post-freeze comparison with exact-ID historical HSA/JIN provenance."""
import json
import zipfile
import milal_mfr_common as cm
from milal_mfr01b_data import digest

STATUSES = ('AGREES_WITH_HISTORICAL', 'PARTIALLY_AGREES', 'HISTORICAL_MORE_SPECIFIC',
            'MFR_MORE_CONSERVATIVE', 'CONFLICTS', 'NO_HISTORICAL_COMPARISON')


def load(out, config):
    from milal_mfr02a_pipeline import freeze_valid
    cm.require(freeze_valid(out), 'Historical access requires verified decision freeze')
    archive=cm.ROOT/config['archive'];cm.require(digest(archive)==config['sha256'],'Historical ZIP changed')
    with zipfile.ZipFile(archive) as z:
        cm.require(z.testzip() is None,'Historical ZIP CRC')
        data=z.read(config['member']);cm.require(cm.sha(data)==config['member_sha256'],'Historical member changed')
    cm.write(out/'historical_source.csv',data)
    return cm.rows(data),{config['archive']:digest(archive),config['member']:cm.sha(data)}


def classify(decision, historical_relation, exact):
    equivalent={'SAME_LEVEL_SIBLING':'PARATACTIC','CHILD_OF':'HYPOTACTIC','HIERARCHICALLY_ABOVE':'HYPOTACTIC','EMBEDDING':'EMBEDDING'}
    h=equivalent.get(historical_relation)
    if h is None:return 'HISTORICAL_MORE_SPECIFIC'
    if decision==h:return 'AGREES_WITH_HISTORICAL' if exact else 'PARTIALLY_AGREES'
    if decision in ('FORMAL_ONLY','INSUFFICIENT'):return 'MFR_MORE_CONSERVATIVE' if exact else 'NO_HISTORICAL_COMPARISON'
    return 'CONFLICTS' if exact else 'NO_HISTORICAL_COMPARISON'


def compare(decisions, historical):
    result=[]
    unresolved=[h['historical_relation_id'] for h in historical if any(h['historical_source']['record'][k]=='UNRESOLVED' for k in ('source_clause_id','target_clause_id'))]
    for d in decisions:
        left=set(d['source_clause_ids']);right=set(d['target_clause_ids']);matches=[]
        for h in historical:
            record=h['historical_source']['record']
            def nodes(key):
                values=record[key]
                if values=='UNRESOLVED':return set()
                cm.require(isinstance(values,list),'Historical endpoint schema')
                cm.require(all(v.startswith('BHSA2021:clause:') for v in values),'Historical clause namespace')
                return {v.removeprefix('BHSA2021:clause:') for v in values}
            hs,ht=nodes('source_clause_id'),nodes('target_clause_id')
            for a,b,orientation in ((hs,ht,'STORED'),(ht,hs,'REVERSED_FOR_COMPARISON')):
                # One whole endpoint must be equal and the other exactly included.
                # Mere overlap, text similarity and reference resemblance never join.
                exact=bool(left and right) and left==a and right==b
                partial=bool(left and right) and ((left==a and right<b) or (left<a and right==b))
                if not (exact or partial):continue
                matches.append(dict(historical_relation_id=h['historical_relation_id'],
                    historical_relation_type=h['historical_relation_type'],orientation=orientation,
                    endpoint_basis='EXACT_CLAUSE_ID_SETS' if exact else 'ONE_EXACT_ENDPOINT_OTHER_EXPLICIT_SUBSET',
                    historical_source_clause_ids=sorted(a),historical_target_clause_ids=sorted(b),
                    historical_review_status=h['historical_review_status'],
                    historical_row_sha256=cm.sha(cm.js(h)),
                    status=classify(d['researcher_decision'],h['historical_relation_type'],exact)))
                break
        statuses={m['status'] for m in matches}
        priority=('CONFLICTS','PARTIALLY_AGREES','MFR_MORE_CONSERVATIVE','HISTORICAL_MORE_SPECIFIC','AGREES_WITH_HISTORICAL')
        status=next((s for s in priority if s in statuses),'NO_HISTORICAL_COMPARISON')
        result.append(dict(decision_id=d['decision_id'],configuration_case_id=d['configuration_case_id'],
            mfr_decision=d['researcher_decision'],status=status,historical_matches=matches,
            historical_unresolved_endpoint_relation_ids=unresolved,
            comparison_scope='HSA_HISTORICAL_RELATIONS_WITH_JIN_0_7_TYPING_AND_REVIEW_PROVENANCE',
            identity_equivalence_asserted=False,decisions_modified=False,
            limitations='POSTFREEZE_ONLY; PARTIAL_ENDPOINTS_ARE_SCOPE_COMPARISON_NOT_OBJECT_IDENTITY; NO_MATCH_IS_NOT_HISTORICAL_REJECTION'))
    return result
