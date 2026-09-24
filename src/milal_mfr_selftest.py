"""Executable method controls built from artificial surface observations."""
import json
from copy import deepcopy
import milal_mfr_common as cm
from milal_mfr_synthetic import corpus
from milal_mfr_observation import observe
from milal_mfr_blind import build
from milal_mfr_relation_candidates import relations

def model(raw=None):
    rules=json.loads((cm.ROOT/'config/mfr_0_1_blind_rules.json').read_bytes());obs=observe(raw or corpus());m=build(obs,rules,'XM');m['relations']=list(relations(m['markers'],obs,m['force'],m['coverage'],m['pairs'],rules,'XM'));return m

def behavior():
    m=model();rr=m['relations'];cross=[r for r in rr if r['cross_book']];labels={l for r in cross for l in r['relation_candidates']}
    raw=corpus()
    for c in raw:c['book']='Changed';c['chapter']+=100;c['verse']+=200
    changed=model(raw)
    projection=lambda x:[(r['source_marker_id'],r['target_marker_id'],r['relation_candidates']) for r in x['relations']]
    other=corpus();other[4]['words'][0]['lex']='XQR[';different=model(other)
    ids={m['marker_id']:m['clause_id'] for m in different['markers']}
    return dict(metadata_invariance=projection(m)==projection(changed),singleton=any(x['singleton_reason'] and 'EXPLICIT_CESSATION' in x['discovery_sources'] for x in m['markers']),
        same_form=all(not r['automatic_resolution'] and 'selected_relation' not in r for r in rr),coverage_multiple=len({r['end_basis'] for r in m['coverage'] if r['marker_id']==m['markers'][0]['marker_id']})>1,
        no_winner=all(not r['automatic_resolution'] and 'selected_root' not in r and 'selected_relation' not in r for r in m['coverage']+rr),cross_book=bool(cross),
        cross_formal='FORMAL_PARALLEL_CANDIDATE' in labels,cross_parataxis='PARATAXIS_CANDIDATE' in labels,cross_hypotaxis='HYPOTAXIS_CANDIDATE' in labels,cross_resumption='RESUMPTION_CANDIDATE' in labels,
        different_form=any(ids[r['source_marker_id']]==101 and ids[r['target_marker_id']]==105 and 'PARATAXIS_CANDIDATE' in r['relation_candidates'] for r in different['relations']))

if __name__=='__main__':
    facts=behavior();print(json.dumps(facts));cm.require(all(facts.values()),'synthetic method contract failed')
