"""Small self-contained prior-stage fixture with all ten contract examples."""
from copy import deepcopy
import milal_jin_io as io
import milal_jin_layer_freeze as prior
from milal_jin_layer_freeze_fixture import fixture as prior_fixture


def fixture(cfg):
    cfg=deepcopy(cfg);pf,pc=prior_fixture(prior.config())
    rows=io.rows(pf[prior.INVENTORY])
    for r in rows:
        r['historical_layer']='TEXTUAL_SAME_LEVEL' if r['relation_type']=='SAME_LEVEL_SIBLING' else 'TEXTUAL_HIERARCHY'
    for rid,src,tgt,typ,layer in [
        ('SYN:NEG','37:24','38:1','NO_DIRECT_PARENTAGE','NEGATIVE_CONSTRAINT'),
        ('SYN:OV','32:1','38:1','CONTRASTIVE_ANA_FRAME','OVERLAY_RESPONSIO'),
        ('SYN:CLOSE','31:40','29:1','DIRECT_LOCAL_CLOSURE','TEXTUAL_HIERARCHY'),
        ('SYN:COMP','31:40','27:1–31:40','TERMINATES_ENCLOSING_GROUP','COMPOSITION_GROUPING'),
        ('SYN:TRANS','31:40','32:1','POST_CLOSURE_TRANSITION','TRANSITION'),
        ('SYN:INTRO','2:11','1:1–2:13','GROUP_MEMBER_OF','COMPOSITION_GROUPING'),
        ('SYN:32','32:1','32:1','TRANSITION_COMPONENT','TRANSITION')]:
        rows.append(dict(relation_id=rid,source_ref=src,target_ref=tgt,relation_type=typ,historical_layer=layer,proposal_status='UNREVIEWED',historical_status='ACCEPTED_SOURCE',latest_review_status='UNREVIEWED',proposed_semantics='NON_PARENT'))
    from collections import Counter
    pc['expected_registry_count']=len(rows);pc['expected_counts']=dict(Counter(r['relation_type'] for r in rows))
    pf[prior.INVENTORY]=io.csv_bytes(rows);io.seal(pf)
    req=(prior.ROOT/pc['source_request']['path']).read_bytes();m=prior.build(pf,pc,req)
    f=prior.render(m,pc,req)
    f['90_run_metadata.json']=io.js(dict(mother_status=m['mother_status'],participant_arc=m['participant_arc']))
    f['history/jin_0_6/24_contextual_human_review_cases.csv']=io.csv_bytes([dict(review_case_id='SYN:REVIEW1',relation_family='HYPOTAXIS',review_status='UNREVIEWED'),dict(review_case_id='SYN:REVIEW2',relation_family='PARATAXIS',review_status='UNREVIEWED')])
    f['history/jin_0_6/01_jin_human_batch1_decisions.csv']=io.csv_bytes([dict(batch_case_id='SYN:B1',relation_decision='PARATACTIC',contextual_review_case_ids=['SYN:REVIEW2'])])
    io.seal(f);cfg['expected_registry_count']=len(rows);cfg['expected_applications']=len(m['applications'])
    return f,cfg
