"""Overlapping formal families; membership is correspondence evidence only."""
from collections import defaultdict
from milal_mfr_signatures import key

FAMILY_RESOLUTIONS={'EXACT_FORM_FAMILY':'SIG_EXACT','SLOT_NORMALIZED_FAMILY':'SIG_LEXICAL_SLOT','CONSTRUCTION_FAMILY':'SIG_CONSTRUCTION','ADJUNCT_EXPANSION_FAMILY':None,'MULTI_CLAUSE_CONFIGURATION_FAMILY':'SIG_SEQUENCE_3','PARTIAL_FORMAL_FAMILY':None,'LEXICAL_RESUMPTION_FAMILY':None}

def families(markers,obs,prefix):
    groups=defaultdict(list);definitions={}
    for m in markers:
        c=obs[m['sequence_index']]
        for typ,res in FAMILY_RESOLUTIONS.items():
            if res:definition=m['signatures'][res]
            elif typ=='ADJUNCT_EXPANSION_FAMILY':definition=m['base_construction']
            elif typ=='PARTIAL_FORMAL_FAMILY':
                constructions=[tag for tag in m['discovery_sources'] if tag in ('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION','REVELATION_HEADING_CONFIGURATION','YEAR_ONE_CONFIGURATION','AFTER_DEATH_TEMPORAL_CONSTRUCTION')]
                definition=dict(explicit_constructions=constructions) if constructions else dict(predicate=c['predicate_lexeme'],conjugation=c['verbal_conjugation'],core=m['base_construction']['core_order'])
            else:definition=dict(predicates=c['predicate_lexeme'],participants=c['participant_surface_set'])
            if not res and not c['predicate_lexeme'] and not (typ=='PARTIAL_FORMAL_FAMILY' and constructions):continue
            k=(typ,key(definition));groups[k].append(m);definitions[k]=definition
    registry=[];membership=[]
    for n,(k,mm) in enumerate(sorted(groups.items()),1):
        fid=prefix+str(n).zfill(5);typ=k[0];variants=sorted({key(m['extension_features']) for m in mm})
        positions=[m['sequence_index'] for m in mm]
        registry.append(dict(family_id=fid,family_type=typ,construction_definition=definitions[k],signature_resolution=FAMILY_RESOLUTIONS[typ] or 'BASE_FEATURE_BUNDLE',occurrence_count=len(mm),marker_ids=[m['marker_id'] for m in mm],occurrence_positions=positions,recurrence_gaps=[b-a for a,b in zip(positions,positions[1:])],variant_signatures=variants,automatic_resolution=False,status='UNADJUDICATED',membership_semantics='FORMAL_CORRESPONDENCE_ONLY'))
        for m in mm:
            m['family_ids'].append(fid);membership.append(dict(family_id=fid,marker_id=m['marker_id'],clause_atom_ids=m['clause_atom_ids'],base_construction=m['base_construction'],extension_features=m['extension_features'],added_adjuncts=m['added_adjuncts'],removed_adjuncts=m['removed_adjuncts']))
    return registry,membership
