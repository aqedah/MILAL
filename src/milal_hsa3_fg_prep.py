"""HSA3-FG-PREP: source evidence only; no human or structural adjudication."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from functools import lru_cache
from pathlib import Path
import sys

import milal_hsa3_abc_seam_adjudication as prior
import milal_hsa3_ana_response_frame as ana
import milal_mr1_surface_marker_provenance as mr1

ROOT, sha, rows, util = prior.ROOT, prior.sha, prior.rows, prior.util
rows = lru_cache(maxsize=32)(rows)
CONFIG = ROOT / 'config/hsa3_fg_prep_job.json'
HISTORY = 'history/hsa3_abc/'
NODES, EDGES, REGISTRY, SEAMS = (prior.HISTORY + x for x in (prior.NODES, prior.EDGES, prior.REGISTRY, prior.SEAMS))
REVIEW_FIELDS = prior.REVIEW_FIELDS
EXTRA = ('lex0', 'gloss', 'txt', 'mother', 'rela', 'code', 'tab', 'pargr')
OUTPUTS = {'01_narratorial_frame_spine.csv':'spine', '02_temporal_expression_inventory.csv':'temporal',
 '03_wayhi_wayyiqtol_frame_comparison.csv':'way', '04_repeated_scene_configuration_1_6_1_13_2_1.csv':'scenes',
 '05_answer_add_formula_shift_audit.csv':'formulas', '06_seam_f_response_complex_evidence.csv':'f',
 '07_seam_f_candidate_compositions.csv':'candidates', '08_seam_g_final_narrative_evidence.csv':'g',
 '09_job_42_7_16_temporal_comparison.csv':'comparison', '10_negative_controls.csv':'negative',
 '13_clause_evidence.csv':'evidence', '14_criteria_crosswalk.csv':'criteria', '15_frozen_integrity.csv':'integrity'}


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-FG-PREP STOP: ' + message)


def refkey(ref):
    return tuple(map(int, ref.split(':')))


def native_bhsa(path):
    path = Path(path).resolve()
    b, execution = mr1.load_bhsa(path, json.loads(mr1.CONFIG.read_bytes()))
    for f in EXTRA:
        p = path / (f + '.tf')
        require(p.is_file(), 'missing feature ' + f)
        require('@version=2021' in p.read_text(encoding='utf-8').split('\n\n', 1)[0].splitlines(), 'feature version ' + f)
        execution['feature_versions'][f] = '2021'
    require(b.T.api.TF.load(' '.join(EXTRA), add=True, silent='deep'), 'additional TF features')
    api = b.T.api.TF.api
    cc = []
    for c in b.clauses:
        ww = list(api.L.d(c, otype='word'))
        atoms = list(api.L.d(c, otype='clause_atom'))
        words = [dict(node=w, reference=':'.join(map(str, api.T.sectionFromNode(w)[1:])), surface=api.T.text((w,)),
                      clause_atom_ids=list(api.L.u(w, otype='clause_atom')), phrase_ids=list(api.L.u(w, otype='phrase')),
                      **{f:getattr(api.F, f).v(w) for f in ana.FEATURES}) for w in ww]
        phrases = [dict(node=p, function=api.F.function.v(p), type=api.F.typ.v(p), word_nodes=list(api.L.d(p, otype='word')),
                        surface=api.T.text(api.L.d(p, otype='word'))) for p in api.L.d(c, otype='phrase')]
        corroboration = [dict(node=n, node_type=api.F.otype.v(n), mother=list(api.E.mother.f(n)),
                             **{f:getattr(api.F, f).v(n) for f in ('rela','code','tab','pargr')}) for n in [c] + atoms]
        cc.append(dict(clause=c, ref=words[0]['reference'], words=words, phrases=phrases, surface=api.T.text(ww),
                       clause_atom_ids=atoms, type=api.F.typ.v(c), domain=api.F.domain.v(c), txt=api.F.txt.v(c),
                       corroboration=corroboration))
    execution['book_word_nodes'] = list(api.L.d(execution['book_node'], otype='word'))
    for name, feature in api.TF.features.items():
        fp = path / (name + '.tf')
        if feature.dataLoaded and fp.is_file():
            execution['data_hashes'][str(fp)] = sha(fp.read_bytes())
    return cc, execution


def load(self_test=False, tf_data=None):
    cfg = json.loads(CONFIG.read_bytes())
    commit = prior.d.baseline_receipt(cfg)
    frozen = prior.d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual'] == r['expected'] for r in frozen), 'frozen repository files')
    request = (ROOT / cfg['source_request']['path']).read_bytes()
    require(sha(request) == cfg['source_request']['sha256'], 'request SHA')
    if self_test:
        ps = prior.load(True)
        files = prior.serialize(prior.build(ps), ps)
        digest = sha(files['99_manifest_sha256.csv'])
        from milal_hsa3_fg_synthetic import fixture
        native, execution, mf = fixture(cfg, rows(files[NODES]))
    else:
        require(tf_data is not None, '--tf-data required')
        data = (ROOT / cfg['archive']['path']).read_bytes()
        digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'A/C ZIP SHA')
        files = prior.d.h.f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
        require(len(files) == cfg['archive']['members'], 'A/C member count')
        pin = cfg['mr1_archive']
        mf = prior.d.h.f.a.prep.r43.h1.src.archive((ROOT / pin['path']).read_bytes(), pin['sha256'], mr1=True)['files']
        require(all(g['status'] == 'PASS' for g in rows(mf['09_gates.csv'])), 'MR1 gates')
        native, execution = native_bhsa(tf_data)
    require(util.manifest_ok(files) and all(r['valid'] for r in prior.d.h.nested_manifests(files)), 'frozen manifests')
    meta = json.loads(files['90_run_metadata.json'])
    require(meta['version'] == 'HSA3-A/C' and meta['status'] == 'PASS' and not meta['r44_started'], 'A/C stage')
    require(all(g['status'] == 'PASS' for g in rows(files['10_gates.csv'])), 'A/C gates')
    s = dict(cfg=cfg, commit=commit, frozen=frozen, request=request, files=files, native=native, execution=execution,
             mr_files=mf, input_sha256=digest, mode='SYNTHETIC_ONLY' if self_test else 'REAL_BHSA_2021_AUDIT')
    validate(s)
    return s


def validate(s):
    cc = s['native']
    require(len({c['clause'] for c in cc}) == len(cc) and cc, 'unique clause identity')
    ww = [w['node'] for c in cc for w in c['words']]
    require(len(set(ww)) == len(ww) and sorted(ww) == sorted(s['execution']['book_word_nodes']), 'whole-book word coverage')
    for c in cc:
        require(all(k in c for k in ('clause','ref','words','phrases','surface','clause_atom_ids','type','domain','txt','corroboration')), 'clause schema')
        require(all(all(k in w for k in ana.FEATURES + ('node','reference','surface','phrase_ids','clause_atom_ids')) for w in c['words']), 'word schema')
        require(all(set(p['word_nodes']) <= {w['node'] for w in c['words']} for p in c['phrases']), 'phrase word identity')
    required = set(sum((s['cfg'][key] for key in ('spine_refs','f_refs','g_refs','formula_refs','way_refs')), []))
    require(required <= {w['reference'] for c in cc for w in c['words']}, 'required locus absent')


def selected(cc, refs):
    return [c for c in cc if set(refs) & {w['reference'] for w in c['words']}]


def words_at(s, ref):
    return [w for c in s['native'] for w in c['words'] if w['reference'] == ref]


def matches(words, pattern):
    return [dict(word_nodes=[w['node'] for w in words[i:i+len(pattern)]], surface=''.join(w['surface'] for w in words[i:i+len(pattern)]))
            for i in range(len(words)-len(pattern)+1) if [w['lex'] for w in words[i:i+len(pattern)]] == pattern]


def source_link(s, member, field, ident):
    rr = prior.d.h.raw_rows(s['files'][member])
    hits = [(i, r) for i, r in enumerate(rr, 1) if r[field] == ident]
    require(len(hits) == 1, 'exact frozen identity ' + ident)
    i, r = hits[0]
    return dict(member=HISTORY+member, data_row=i, identity_field=field, identity=ident,
                row_sha256=prior.d.h.f.rowhash(r), member_sha256=sha(s['files'][member]), artifact_sha256=s['input_sha256'])


def accepted(s, clause):
    anchor = 'BHSA2021:clause:' + str(clause)
    synthetic = next((c.get('synthetic_anchor') for c in s['native'] if c['clause']==clause),None) if s['mode']=='SYNTHETIC_ONLY' else None
    nn = [n for n in rows(s['files'][NODES]) if anchor in n['source_evidence_ids'] or (synthetic and synthetic in n['source_evidence_ids'])]
    ids = {n['node_id'] for n in nn}
    ee = [e for e in rows(s['files'][EDGES]) if e['source_node'] in ids or e['target_node'] in ids]
    return dict(nodes=nn, relations=ee, source_links=[source_link(s, NODES, 'node_id', n['node_id']) for n in nn])


def positions(c, p):
    ids = [w['node'] for w in c['words']]
    pos = [ids.index(n)+1 for n in p['word_nodes']]
    verbs = [i+1 for i, w in enumerate(c['words']) if w['sp'] == 'verb']
    return dict(word_positions=pos, clause_initial=min(pos)==1, before_first_verb=bool(verbs and max(pos)<min(verbs)),
                after_first_verb=bool(verbs and min(pos)>min(verbs)))


def evidence(s):
    out = []
    lx = s['cfg']['lexemes']
    for i, c in enumerate(s['native']):
        ww = c['words']; ids = {w['node']:w for w in ww}
        subj = [p for p in c['phrases'] if p['function'] == 'Subj']
        obj = [p for p in c['phrases'] if p['function'] in ('Objc','Cmpl')]
        times = [dict(**p, **positions(c,p)) for p in c['phrases'] if p['function']=='Time' or any(ids[w]['lex']==lx['temporal_core'] for w in p['word_nodes'])]
        verbs = [w for w in ww if w['sp']=='verb']
        # Raw lexical morphology, separate from the frozen MR1 Way0 classification.
        wayhi = [w['node'] for j,w in enumerate(ww) if w['lex']==lx['be'] and w['vt']=='wayq' and (w['ps'],w['gn'],w['nu'])==('p3','m','sg') and j>0 and ww[j-1]['lex']=='W']
        live = [w['node'] for j,w in enumerate(ww) if w['lex']==lx['live'] and w['vt']=='wayq' and (w['ps'],w['gn'],w['nu'])==('p3','m','sg') and j>0 and ww[j-1]['lex']=='W']
        mentions = [w for w in ww if w['sp']=='nmpr' or w['lex']==lx['satan'] or any(w['node'] in p['word_nodes'] and w['sp'] in ('subs','prps','prde') for p in subj)]
        historic = accepted(s, c['clause'])
        out.append(dict(evidence_id='FG:C:'+str(c['clause']), reference=c['ref'], clause_node=c['clause'], clause_atom_nodes=c['clause_atom_ids'],
            exact_surface=c['surface'], clause_type=c['type'], domain=c['domain'], txt=c['txt'],
            narrator_evidence='BHSA_DOMAIN_N' if c['domain']=='N' else 'BHSA_QUOTED_DOMAIN_Q' if c['domain']=='Q' else 'UNRESOLVED_DOMAIN',
            verbal_words=verbs, subjects=subj, objects_and_complements=obj, participant_surface_mentions=mentions,
            participant_identity_policy='EXPLICIT_SURFACE_ONLY; NO_COREFERENCE_ASSIGNMENT', phrase_functions=c['phrases'], temporal_expressions=times,
            conjunctions=[p for p in c['phrases'] if p['function']=='Conj'], lexical_wayhi_words=wayhi, lexical_waychi_words=live,
            preceding_clause=dict(clause=s['native'][i-1]['clause'],type=s['native'][i-1]['type']) if i else {},
            following_clause=dict(clause=s['native'][i+1]['clause'],type=s['native'][i+1]['type']) if i+1<len(s['native']) else {},
            current_hsa=historic, source_provenance_ids=[('SYNTHETIC' if s['mode']=='SYNTHETIC_ONLY' else 'BHSA2021')+':clause:'+str(c['clause'])]+[('SYNTHETIC' if s['mode']=='SYNTHETIC_ONLY' else 'BHSA2021')+':word:'+str(w['node']) for w in ww],
            source_snapshot='16_bhsa_source_snapshot.json', source_record_sha256=prior.d.h.f.rowhash(c),
            post_discovery_corroboration=c['corroboration'], corroboration_use='NEVER_CONVERTED_TO_MILAL_PARENTAGE'))
    return out


def inventory(s, ev):
    lookup = {r['clause_node']:r for r in ev}; out=[]; lx=s['cfg']['lexemes']
    scopes = rows(s['files']['03_hsa3_abc_composition_groups.csv'])
    for c in s['native']:
        for w in c['words']:
            if w['lex'] not in (lx['temporal_core'], lx['other_homonym']):
                continue
            pp=[p for p in c['phrases'] if w['node'] in p['word_nodes']]
            require(len(pp)==1,'temporal token exact phrase')
            p=pp[0]
            if w['lex']==lx['other_homonym']:
                sense='NON_TEMPORAL_OTHER_HOMONYM'; basis='Distinct BHSA lexeme >XR=/, not the after lexeme.'
            elif p['function']=='Time':
                sense='TEMPORAL_SUPPORTED'; basis='Explicit BHSA Time phrase.'
            elif p['function']=='Conj' and c['words'][0]['node']==w['node'] and any(v['sp']=='verb' and v['vt']=='perf' for v in c['words'][1:]):
                sense='TEMPORAL_SUPPORTED'; basis='Clause-initial after lexeme as Conj preceding an overt perfect verb; no mother relation used.'
            else:
                sense='UNRESOLVED_SENSE'; basis='Time vs spatial/other reading not settled by permitted phrase/morphological evidence; retain candidate.'
            accepted_nodes=lookup[c['clause']]['current_hsa']['nodes']
            node_ids={n['node_id'] for n in accepted_nodes}
            continuation=[e for e in lookup[c['clause']]['current_hsa']['relations'] if e['source_node'] in node_ids and e['relation_type']=='CONTINUES_WITHIN']
            scope_hits=[g['group_id'] for g in scopes if refkey(g['span_start'])<=refkey(w['reference'])<=refkey(g['span_end'])]
            out.append(dict(occurrence_id='FG:W:'+str(w['node']), reference=w['reference'], word_node=w['node'], clause_node=c['clause'],
                lexical_form=w['lex'], lex_utf8=w['lex_utf8'], exact_surface=w['surface'], phrase=p, **positions(c,p),
                sense=sense, classification_basis=basis, clause_type=c['type'], current_hsa_nodes=accepted_nodes,
                current_boundary_assertions=[n['node_id'] for n in accepted_nodes if n['textual_boundary']],
                accepted_no_boundary=[n['node_id'] for n in accepted_nodes if 'NO_BOUNDARY' in n['all_historical_functions'] or n['structural_function']=='NO_BOUNDARY'],
                established_scope_positional_hits=scope_hits, accepted_continuation_relations=continuation,
                established_unit_status='EXPLICIT_CONTINUATION' if continuation else 'POSITION_WITHIN_RESEARCHER_GROUP' if scope_hits else 'NOT_ESTABLISHED_FROM_PERMITTED_EVIDENCE',
                scope_policy='POSITION_WITHIN_EXPLICIT_HUMAN_SPANS_ONLY; NOT_NEW_MEMBERSHIP_OR_PARENTAGE',
                structural_implication='NOT_ADJUDICATED', evidence_id=lookup[c['clause']]['evidence_id']))
    return out


def verse_panel(s, ev, refs):
    by={c['clause']:c for c in s['native']}
    return [deepcopy(e) for e in ev if any(w['reference'] in refs for w in by[e['clause_node']]['words'])]


def scene_audit(s):
    out=[];patterns=s['cfg']['patterns'];lx=s['cfg']['lexemes']
    for start,end in s['cfg']['scene_windows']:
        cc=[c for c in s['native'] if refkey(start)<=refkey(c['ref'])<=refkey(end)]
        ww=[w for c in cc for w in c['words']]
        dialogue=[c for c in cc if lx['say'] in [w['lex'] for w in c['words']] and lx['yhwh'] in [w['lex'] for w in c['words']] and lx['satan'] in [w['lex'] for w in c['words']]]
        out.append(dict(start_ref=start,end_ref=end,opening_day=matches(words_at(s,start),patterns['day']),
            sons_of_god=matches(ww,patterns['sons_of_god']),stand_before_yhwh=matches(ww,patterns['stand_before_yhwh']),
            satan_words=[w['node'] for w in ww if w['lex']==lx['satan']],divine_satan_speech_clauses=[c['clause'] for c in dialogue],
            ordered_clauses=[dict(clause=c['clause'],reference=c['ref'],type=c['type'],surface=c['surface'],lexemes=[w['lex'] for w in c['words']]) for c in cc],
            existing_judgments=[accepted(s,c['clause']) for c in selected(cc,[start])], structural_implication='SIMILAR_OPENING_NOT_SUFFICIENT_FOR_SAME_LEVEL',new_relation_ids=[]))
    return out


def formula_audit(s, refs):
    lx=s['cfg']['lexemes'];out=[]
    mr=rows(s['mr_files']['02_csf_reproduction.csv'])
    for ref in refs:
        ww=words_at(s,ref);cc=selected(s['native'],[ref]);verbs=[w for w in ww if w['sp']=='verb']
        first=verbs[0]['lex'] if verbs else None
        family='ANSWER' if first==lx['answer'] else 'ADD' if first==lx['add'] else 'OTHER'
        out.append(dict(reference=ref,exact_surface=''.join(w['surface'] for w in ww),clause_ids=[c['clause'] for c in cc],
            verbal_sequence=[dict(node=w['node'],lex=w['lex'],vt=w['vt'],surface=w['surface']) for w in verbs],formula_family=family,
            take_proverb=matches(ww,s['cfg']['patterns']['take_proverb']),current_hsa=[accepted(s,c['clause']) for c in cc],
            historical_csf=[r for r in mr if int(r['start_clause']) in {c['clause'] for c in cc}],
            distribution_context='EXACT_ACCEPTED_GROUP_MEMBERSHIPS_IN_CURRENT_HSA_RECORDS',
            structural_implication='SAME_FORMAL_SHIFT_DOES_NOT_ENTAIL_SAME_STRUCTURAL_FUNCTION'))
    return out


def candidates():
    specs=[('FG-F-C1','YHWH_JOB_RESPONSE_COMPLEX_1','38:1–40:5'),('FG-F-C2','YHWH_JOB_RESPONSE_COMPLEX_2','40:6–42:6'),('FG-F-C3','POSSIBLE_SAME_LEVEL_COMPOSITION_PEERS','FG-F-C1 / FG-F-C2')]
    return [dict(candidate_id=i,label=label,possible_span=span,status='UNADJUDICATED',automatic_resolution=False,
                 new_relation_ids=[],**{f:'UNREVIEWED' if f=='review_status' else '' for f in REVIEW_FIELDS}) for i,label,span in specs]


def comparison(s, ev, inv):
    out=[]
    for ref in ('3:1','42:7','42:16'):
        hits=[r for r in inv if r['reference']==ref and r['lexical_form']==s['cfg']['lexemes']['temporal_core']]
        require(len(hits)==1,'temporal comparison exact occurrence '+ref)
        e=next(e for e in ev if e['clause_node']==hits[0]['clause_node'])
        out.append(dict(reference=ref,exact_verse_surface=''.join(w['surface'] for w in words_at(s,ref)),temporal_occurrence=hits[0],
            SIMILARITY='Same verified after lexeme; temporal reading supported in this local construction.',
            DIFFERENCE=dict(phrase_function=hits[0]['phrase']['function'],clause_type=e['clause_type'],word_positions=hits[0]['word_positions'],clause_initial=hits[0]['clause_initial'],before_first_verb=hits[0]['before_first_verb'],after_first_verb=hits[0]['after_first_verb'],verbal_lexemes=[w['lex'] for w in e['verbal_words']]),
            STRUCTURAL_IMPLICATION='NO_AUTOMATIC_BOUNDARY_OR_HIERARCHY; REVIEW_ONLY',
            CURRENT_JUDGMENT=[n for r in verse_panel(s,ev,[ref]) for n in r['current_hsa']['nodes']],
            counter_evidence_for_review=dict(temporal_expression=hits[0]['phrase']['surface'],overt_subject=e['subjects'],clause_form=e['clause_type'],possible_life_summary_shift='POSSIBLE_REVIEW_DESCRIPTION_NOT_JUDGMENT' if any(w['lex']==s['cfg']['lexemes']['live'] for w in e['verbal_words']) else 'NOT_ASSERTED')))
    return out


def negative_controls(s, m):
    return [dict(control_id=i,observations=obs,prohibited_inference=ban,status='EVIDENCE_ONLY') for i,obs,ban in [
      ('TEMPORAL',m['comparison'],'same temporal lexeme = same boundary'),
      ('WAYHI_WAYCHI',m['way'],'lexical prefix similarity = identical verb'),
      ('SCENE',m['scenes'],'identical opening = same level'),
      ('FORMAL_SHIFT',[r for r in m['formulas'] if r['reference'] in ('27:1','36:1')],'same formal shift = same structural transition'),
      ('F_REPETITION',[r for r in m['f'] if r['reference'] in ('38:3','40:7')],'repeated imperative = automatic parent/sibling'),
      ('FINAL_NARRATIVE',m['g'],'narrator/temporal/longer formula = boundary/higher level')]]


def review_packet(m):
    lines=['# HSA3-FG-PREP evidence packet','',
      'Source dataset: '+m['execution']['bhsa_version']+'; Text-Fabric: '+m['execution']['tf_version']+'. Synthetic fixtures are invented mechanics tests, not empirical Hebrew evidence.',
      'A–E remain FROZEN; F/G remain UNREVIEWED. No new human judgment, accepted overlay, textual relation or R4.4.',
      'Narratorial Frame Spine is a testing/reporting overlay, not a composition group, parent, or new structural relation.',
      'Same marker ≠ same structural function; same temporal lexeme ≠ same boundary; same formal shift ≠ same structural transition; narratorial clause ≠ automatic higher-level clause.', '',
      '## Temporal comparison','', '| Locus | Exact surface | Phrase / position | Current judgment |', '| --- | --- | --- | --- |']
    for r in m['comparison']:
        d=r['DIFFERENCE']; labels=sorted({label for n in r['CURRENT_JUDGMENT'] for label in (n['all_historical_functions'] or [n['structural_function']])})
        lines.append(f"| {r['reference']} | {r['exact_verse_surface']} | {d['phrase_function']}; words {d['word_positions']}; before verb {d['before_first_verb']}; after verb {d['after_first_verb']} | {', '.join(labels)} |")
    lines += ['', 'Whole-book narrow lexeme inventory: '+json.dumps(dict(Counter(r['sense'] for r in m['temporal'])),sort_keys=True)+'.',
      'UNRESOLVED_SENSE is retained rather than forcing a temporal/spatial interpretation. Derivatives such as אחרית are outside the narrow אחר/אחרי inventory, and remain in the source snapshot.', '',
      '## Scene and formula controls','']
    for r in m['scenes']:
        lines.append(f"- {r['start_ref']}–{r['end_ref']}: day opening {len(r['opening_day'])}; sons-of-God matches {len(r['sons_of_god'])}; standing matches {len(r['stand_before_yhwh'])}; divine–satan speech clauses {r['divine_satan_speech_clauses']}.")
    for r in m['formulas']:
        lines.append(f"- {r['reference']}: {r['formula_family']}; {r['exact_surface']}; take-proverb phrase matches {len(r['take_proverb'])}.")
    lines += ['', 'The 27:1 and 36:1 forms are compared to preceding ANSWER-type onsets; accepted memberships, not formula expansion, distinguish their structural contexts.', '',
      '## Focused F/G evidence','', '| Locus | Clause / type / domain | Exact surface | Surface subjects and target phrases |', '| --- | --- | --- | --- |']
    for e in m['f']+m['g']:
        lines.append(f"| {e['reference']} | {e['clause_node']} / {e['clause_type']} / {e['domain']} | {e['exact_surface']} | {'; '.join(p['surface'] for p in e['subjects']+e['objects_and_complements'])} |")
    lines += ['', '42:16 retains temporal אחרי זאת, overt Job, חיה wayyiqtol and the possible life-summary shift as review evidence. These are countervailing observations to examine, not an adjudicated contradiction of NO_BOUNDARY. No evidence is suppressed and no promotion is performed.',
      '42:10 and 42:12 retain subject/predicate and participant/state-change evidence, including WXQt forms. Evidence does not independently authorize a major boundary. 42:12 also contains היה wayyiqtol in a later WayX clause; lexical ויהי is separate from the MR1 Way0 audit population.',
      '38:3/40:7 retain the exact repeated imperative and differences in following clauses. These may support comparison of already established peers, never create new parentage.', '',
      '## SEAM_F — researcher question','',
      'Do the established peer pairs support two same-level YHWH–Job response complexes: 38:1–40:5 and 40:6–42:6?', '',
      'Possible outcomes: HUMAN_SUPPLIED_COMPOSITION_RELATION; UNRESOLVED; INSUFFICIENT_EVIDENCE.', '']
    lines += ['| Researcher field | Value |','| --- | --- |']+[f"| {f} | {'UNREVIEWED' if f=='review_status' else ''} |" for f in REVIEW_FIELDS]
    lines += ['', '## SEAM_G — researcher question','',
      'What relation connects the YHWH–Job speech complex ending at 42:6 with the final narrative beginning at 42:7?', '',
      'Internal boundary controls: 42:10, 42:12, 42:16. Existing judgments remain unchanged; no answer is supplied.', '',
      '| Researcher field | Value |','| --- | --- |']+[f"| {f} | {'UNREVIEWED' if f=='review_status' else ''} |" for f in REVIEW_FIELDS]
    lines += ['', '## Traceability','']+[f'- [{name}]({name})' for name in OUTPUTS]
    lines += ['- [Full BHSA source snapshot](16_bhsa_source_snapshot.json)', '- [Frozen F/G packet]('+HISTORY+'09_hsa3_fg_remaining_review_packet.md)', '']
    return '\n'.join(lines)


def derive(s):
    ev=evidence(s); inv=inventory(s,ev)
    needed=set(sum((s['cfg'][k] for k in ('spine_refs','f_refs','g_refs','formula_refs','way_refs')),[]))
    needed.update(r['reference'] for r in inv)
    for start,end in s['cfg']['scene_windows']:
        needed.update(c['ref'] for c in s['native'] if refkey(start)<=refkey(c['ref'])<=refkey(end))
    mrway=rows(s['mr_files']['04_way0_wayhi_reproduction.csv'])
    way=[dict(e, historical_mr1_rows=[r for r in mrway if int(r['start_clause'])==e['clause_node']]) for e in verse_panel(s,ev,s['cfg']['way_refs'])]
    f=verse_panel(s,ev,s['cfg']['f_refs'])
    for e in f:
        c=next(c for c in s['native'] if c['clause']==e['clause_node'])
        e['storm_words']=[w for w in c['words'] if w['lex']==s['cfg']['lexemes']['storm']]
        e['repeated_challenge']=matches(c['words'],s['cfg']['patterns']['challenge'])
        e['historical_csf']=[r for r in rows(s['mr_files']['02_csf_reproduction.csv']) if int(r['start_clause'])==c['clause']]
        speech_predicate=any(w['lex'] in (s['cfg']['lexemes']['answer'],s['cfg']['lexemes']['say'],s['cfg']['lexemes']['add']) for w in e['verbal_words'])
        e['speaker_evidence']=dict(explicit_subject_phrases=e['subjects'] if speech_predicate else [],
            accepted_hsa_speakers=[n['human_speaker'] for n in e['current_hsa']['nodes'] if n['human_speaker']],
            identity_status='EXPLICIT_SPEECH_PREDICATE_SUBJECT' if speech_predicate and e['subjects'] else 'UNRESOLVED_IN_THIS_CLAUSE')
        e['addressee_evidence']=dict(explicit_object_complement_phrases=e['objects_and_complements'] if speech_predicate else [],
            pronominal_verb_features=[dict(word=w['node'],ps=w['prs_ps'],gn=w['prs_gn'],nu=w['prs_nu']) for w in e['verbal_words']],
            referential_identity='NO_UNSTATED_COREFERENCE_ASSIGNED')
        e['csf_type']=[r['historical_projection']['csf_family'] for r in e['historical_csf']]
        e['response_evidence']='FORMULA_AND_EXPLICIT_TARGET_ONLY; SEMANTIC_ANTECEDENT_NOT_ASSIGNED'
    registry={r['evidence_code']:r for r in rows(s['files'][REGISTRY])}
    require(set(s['cfg']['criteria_codes'])<=set(registry),'canonical criteria codes')
    criteria=[dict(evidence_code=code,original_record=registry[code],source_link=source_link(s,REGISTRY,'evidence_code',code),
                   application='DESCRIPTIVE_COMPARISON_ONLY; NEVER_SUFFICIENT_ALONE',panels=list(OUTPUTS)[:10]) for code in s['cfg']['criteria_codes']]
    historical={HISTORY+k:v for k,v in s['files'].items()}|{'history/mr1/'+k:v for k,v in s['mr_files'].items()}
    m=dict(evidence=verse_panel(s,ev,needed),spine=verse_panel(s,ev,s['cfg']['spine_refs']),temporal=inv,way=way,scenes=scene_audit(s),
           formulas=formula_audit(s,s['cfg']['formula_refs']),f=f,g=verse_panel(s,ev,s['cfg']['g_refs']),candidates=candidates(),
           comparison=comparison(s,ev,inv),criteria=criteria,native=deepcopy(s['native']),historical=historical,
           commit=deepcopy(s['commit']),execution=deepcopy(s['execution']),human_judgments=[],textual_relations=[],accepted_overlays=[],
           fg_review=[dict(seam_id=x,**{f:'UNREVIEWED' if f=='review_status' else '' for f in REVIEW_FIELDS}) for x in ('SEAM_F','SEAM_G')],
           r44_started=False,spine_kind='AUDIT_OVERLAY_NOT_STRUCTURAL_OBJECT')
    m['integrity']=[dict(member=k,sha256=sha(v),status='PASS' if historical[k]==v else 'FAIL') for k,v in sorted(historical.items())]
    m['negative']=negative_controls(s,m);m['packet']=review_packet(m)
    return m


def digest(m):
    return prior.d.h.f.rowhash({k:({n:sha(v) for n,v in value.items()} if k=='historical' else value) for k,value in m.items() if k!='rerun_digest'})


def build(s):
    m=derive(s);m['rerun_digest']=digest(derive(s));return m


def gates(m,s):
    expected=derive(s)
    checks={}
    oldedges=rows(s['files'][EDGES])
    currentedges=rows(m['historical'].get(HISTORY+EDGES,s['files'][EDGES]))
    same_member=lambda member: m['historical'].get(HISTORY+member)==s['files'][member]
    has=lambda src,tgt,rel: any(e['source_node']==src and e['target_node']==tgt and e['relation_type']==rel for e in currentedges)
    panel=lambda field,ref:[r for r in m[field] if r['reference']==ref]
    cmp={r['reference']:r for r in m['comparison']}
    fm={r['reference']:r for r in m['formulas']}
    scenes={r['start_ref']:r for r in m['scenes']}
    checks['BASELINE_COMMIT_VERIFIED']=m['commit']==s['commit'] and m['commit']['verified_commit']==s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    checks['ABC_FROZEN']=same_member('01_hsa3_abc_seam_adjudications.csv') and all(r['status']=='FROZEN' for r in rows(s['files']['01_hsa3_abc_seam_adjudications.csv']))
    de=prior.HISTORY+prior.DE
    checks['DE_FROZEN']=same_member(de) and all(r['status']=='FROZEN' for r in rows(s['files'][de]))
    checks['FG_UNREVIEWED']=m['fg_review']==expected['fg_review'] and same_member('13_hsa3_fg_original_cases.csv')
    checks['NO_R4_4']=m['r44_started'] is False
    checks['NO_NEW_HUMAN_JUDGMENT']=m['human_judgments']==[]
    checks['NO_NEW_TEXTUAL_RELATION']=m['textual_relations']==[]
    checks['NO_NEW_ACCEPTED_OVERLAY']=m['accepted_overlays']==[]
    for ref,name,sequence in [('3:1','AFTER_THUS_DETECTED',['>XR/','KN']),('42:7','AFTER_YHWH_SPEAKING_DETECTED',['>XR/','DBR[','JHWH/']),('42:16','AFTER_THIS_DETECTED',['>XR/','Z>T'])]:
        checks[name]=bool(matches([w for c in m['native'] for w in c['words'] if w['reference']==ref],sequence)) and ref in cmp
    live=panel('g','42:16')
    checks['JOB_42_16_LIVE_NOT_BE']=bool(live) and any(w['lex']==s['cfg']['lexemes']['live'] for e in live for w in e['verbal_words']) and not any(w['lex']==s['cfg']['lexemes']['be'] for e in live for w in e['verbal_words'])
    checks['WAYHI_WAYCHI_DISTINCT']=bool(live) and any(e['lexical_waychi_words'] for e in live) and not any(e['lexical_wayhi_words'] for e in live) and m['way']==expected['way']
    checks['TEMPORAL_POSITION_DISTINCT']=set(cmp)=={'3:1','42:7','42:16'} and cmp['3:1']['DIFFERENCE']['before_first_verb'] is True and cmp['42:16']['DIFFERENCE']['after_first_verb'] is True and cmp['42:7']['DIFFERENCE']['phrase_function']=='Conj'
    checks['WHOLE_BOOK_TEMPORAL_COVERAGE']=m['temporal']==expected['temporal'] and len({r['word_node'] for r in m['temporal']})==len(m['temporal'])
    checks['TEMPORAL_NOT_AUTO_BOUNDARY']=all(r['structural_implication']=='NOT_ADJUDICATED' for r in m['temporal']) and not m['textual_relations']
    checks['REPEATED_SCENE_CONFIGURATION']=all(k in scenes and scenes[k]['opening_day'] and scenes[k]['sons_of_god'] and scenes[k]['stand_before_yhwh'] and scenes[k]['satan_words'] and scenes[k]['divine_satan_speech_clauses'] for k in ('1:6','2:1')) and m['scenes']==expected['scenes']
    checks['JOB_1_13_NOT_PROMOTED']='1:13' in scenes and bool(scenes['1:13']['opening_day']) and not scenes['1:13']['sons_of_god'] and not scenes['1:13']['new_relation_ids'] and has('H:HSA003','H:HSA002','CHILD_OF')
    checks['TEST_SCENE_SIBLINGS_PRESERVED']=has('H:HSA002','H:HSA009','SAME_LEVEL_SIBLING') and currentedges==oldedges
    checks['JOB_27_ADD_FORMULA']='27:1' in fm and fm['27:1']['formula_family']=='ADD' and bool(fm['27:1']['take_proverb'])
    checks['JOB_36_ADD_FORMULA']='36:1' in fm and fm['36:1']['formula_family']=='ADD' and not fm['36:1']['take_proverb']
    checks['FORMAL_SHIFT_NOT_STRUCTURAL_EQUIVALENCE']=m['formulas']==expected['formulas'] and all(r['structural_implication']=='SAME_FORMAL_SHIFT_DOES_NOT_ENTAIL_SAME_STRUCTURAL_FUNCTION' for r in m['formulas'])
    checks['YHWH_PEERS_PRESERVED']=has('H:HSA025','H:HSA028','SAME_LEVEL_SIBLING')
    checks['JOB_RESPONSE_PEERS_PRESERVED']=has('H:HSA027','H:HSA029','SAME_LEVEL_SIBLING')
    checks['INTERNAL_40_1_CHILD_PRESERVED']=has('H:HSA026','H:HSA025','CHILD_OF')
    checks['REPEATED_CHALLENGE_CAPTURED']=all(any(r['repeated_challenge'] for r in panel('f',ref)) for ref in ('38:3','40:7')) and m['f']==expected['f']
    checks['F_CANDIDATES_UNADJUDICATED']=m['candidates']==candidates()
    g7=panel('g','42:7')
    checks['JOB_42_7_PARAGRAPH_PRESERVED']=any(n['node_id']=='H:HSA030' and 'PARAGRAPH_ONSET' in n['all_historical_functions'] for r in g7 for n in r['current_hsa']['nodes'])
    for ref,name in [('42:10','JOB_42_10_NOT_PROMOTED'),('42:12','JOB_42_12_NOT_PROMOTED')]:
        checks[name]=bool(panel('g',ref)) and panel('g',ref)==[r for r in expected['g'] if r['reference']==ref] and not m['textual_relations']
    checks['JOB_42_16_NO_BOUNDARY_PRESERVED']=has('H:HSA031','H:HSA031','NO_BOUNDARY') and has('H:HSA031','H:HSA030','CONTINUES_WITHIN') and live==[r for r in expected['g'] if r['reference']=='42:16']
    checks['JOB_42_16_COUNTER_EVIDENCE_RETAINED']='42:16' in cmp and cmp['42:16']==next(r for r in expected['comparison'] if r['reference']=='42:16') and bool(cmp['42:16']['counter_evidence_for_review']['temporal_expression'])
    checks['FORMULA_LENGTH_NOT_HIERARCHY_BASIS']=not m['textual_relations'] and m['negative']==expected['negative']
    checks['NARRATOR_NOT_HIERARCHY_BASIS']=m['spine_kind']=='AUDIT_OVERLAY_NOT_STRUCTURAL_OBJECT' and not m['textual_relations']
    checks['BHSA_MOTHER_CORROBORATION_ONLY']=m['evidence']==expected['evidence'] and all(r['corroboration_use']=='NEVER_CONVERTED_TO_MILAL_PARENTAGE' for r in m['evidence']) and not m['textual_relations']
    checks['FROZEN_ARTIFACTS_UNCHANGED']=m['historical']==expected['historical']
    checks['FROZEN_REPOSITORY_PINS']=len(s['frozen'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    checks['SOURCE_SNAPSHOT_EXACT']=m['native']==s['native'] and m['execution']==s['execution']
    ex=m['execution']; real=s['mode']=='REAL_BHSA_2021_AUDIT'
    checks['BHSA_VERSION_AND_COVERAGE']=sorted(w['node'] for c in m['native'] for w in c['words'])==sorted(ex['book_word_nodes']) and ex['bhsa_version']==('2021' if real else 'SYNTHETIC') and ex['tf_version']==(json.loads(mr1.CONFIG.read_bytes())['tf_version'] if real else 'SYNTHETIC') and (not real or bool(ex['feature_versions']) and all(v=='2021' for v in ex['feature_versions'].values()))
    checks['REQUEST_SOURCE_EXACT']=sha(s['request'])==s['cfg']['source_request']['sha256']
    checks['CRITERIA_CANONICAL']=m['criteria']==expected['criteria']
    checks['PACKET_FAITHFUL']=m['packet']==review_packet(m) and m['spine']==expected['spine']
    checks['INTEGRITY_RECEIPTS_COMPUTED']=m['integrity']==expected['integrity'] and all(r['status']=='PASS' for r in m['integrity'])
    checks['DETERMINISTIC_RERUN']=m['rerun_digest']==digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def counts(m):
    return dict(temporal_family_occurrences=len(m['temporal']),temporal_classes=dict(Counter(r['sense'] for r in m['temporal'])),
      evidence_clauses=len(m['evidence']),source_clauses=len(m['native']),source_words=sum(len(c['words']) for c in m['native']),
      candidate_compositions=len(m['candidates']),new_human_judgment_count=len(m['human_judgments']),
      new_textual_relation_count=len(m['textual_relations']),new_accepted_overlay_relation_count=len(m['accepted_overlays']))


def serialize(m,s):
    gg=gates(m,s)
    require(all(g['status']=='PASS' for g in gg),str([g for g in gg if g['status']=='FAIL']))
    files=dict(m['historical'])
    for name,field in OUTPUTS.items():files[name]=util.csv_bytes(m[field])
    files['11_hsa3_fg_prep_review_packet.md']=m['packet'].encode()
    files['16_bhsa_source_snapshot.json']=util.json_bytes(dict(mode=s['mode'],clauses=m['native'],execution=m['execution']))
    files['17_researcher_request.txt']=s['request']
    files['18_fg_review_fields.csv']=util.csv_bytes(m['fg_review'])
    files['90_run_metadata.json']=util.json_bytes(dict(version='HSA3-FG-PREP',mode=s['mode'],status='PASS',gate_count=len(gg)+1,
        counts=counts(m),baseline_commit=m['commit'],input_sha256=s['input_sha256'],input_archive_pins=dict(abc=s['cfg']['archive'],mr1=s['cfg']['mr1_archive']),execution=m['execution'],frozen_receipts=s['frozen'],
        code_sha256=sha(Path(__file__).read_bytes()),config_sha256=sha(CONFIG.read_bytes()),request_sha256=sha(s['request']),
        rerun_payload_sha256=m['rerun_digest'],r44_started=m['r44_started'],fg_status='UNREVIEWED'))
    def seal():
        files.pop('99_manifest_sha256.csv',None)
        files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])
    seal();gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['12_gates.csv']=util.csv_bytes(gg);seal();require(util.manifest_ok(files),'manifest')
    return files


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true')
    args=p.parse_args(argv);require(not(args.self_test and args.tf_data),'synthetic cannot load real BHSA')
    s=load(args.self_test,args.tf_data);m=build(s);files=serialize(m,s)
    require(prior.d.h.f.a.prep.r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen files changed during execution')
    if not args.self_test:
        require(all(sha(Path(p).read_bytes())==h for p,h in s['execution']['data_hashes'].items()),'BHSA files changed during execution')
        for pin in (s['cfg']['archive'],s['cfg']['mr1_archive']):require(sha((ROOT/pin['path']).read_bytes())==pin['sha256'],'input ZIP changed')
    prior.d.h.f.a.prep.publish(files,args.out)
    out=Path(args.out).resolve();zp=out.with_name(out.name+'_results.zip')
    receipt='HSA3-FG-PREP PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(receipt,encoding='utf-8');print(receipt)
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(2)
