"""Draft dimension-specific review vocabulary; no scoring or adjudicator."""
DIMENSIONS={
 'BOUNDARY_EXISTENCE':dict(question='Is there a structural boundary?',evidence='Explicit onset/closure; repeated framing; participant/time/place shift; syntactic discontinuity; negative or continuation evidence.',prohibited='Chapter boundary alone; thematic change alone.'),
 'STRUCTURAL_FUNCTION':dict(question='What observable structural function does the marker have?',evidence='Speech onset/end, paragraph onset, transition, narrative introduction, or NO_BOUNDARY evaluated in local construction and accepted scope.',prohibited='A marker label or formula alone fixes no function.'),
 'SAME_LEVEL_RELATION':dict(question='Are independently identified unit onsets at the same structural level?',evidence='Same established function, formula correspondence, repeated position, distributional symmetry and intervening units.',prohibited='Formula length alone; same speaker alone.'),
 'PARENTAGE_CONTAINMENT':dict(question='Is one unit directly contained in another?',evidence='Explicit grammatical dependency, independently established enclosing scope, embedded speech onset; relevant BHSA syntax as corroboration only.',prohibited='Adjacency; speaker alternation; response semantics; same lexeme; nearest opening; macro boundary implies parent.'),
 'CLOSURE_TARGET':dict(question='What does an ending marker directly close?',evidence='Distinguish DIRECT_LOCAL_CLOSURE, TERMINATES_ENCLOSING_GROUP, NO_DIRECT_RELATION and UNRESOLVED. HSA2-F at 31:40 is the frozen example.',prohibited='Conflate direct closure with higher-order terminal effect.'),
 'OVERLAY_RESPONSIO':dict(question='Is there a non-hierarchical long-distance correspondence?',evidence='Lexical/family recurrence, participant/addressee alignment, polarity contrast, semantic-role correspondence, explicit request and possible later fulfillment.',prohibited='Recurrence implies hierarchy; adjacency implies antecedent; same root implies response.'),
 'RESPONSE_RELATION':dict(question='What kind of response claim is supported?',evidence='Keep FORMAL_CSF, CONTEXTUAL_RESPONSE, SEMANTIC_RESPONSE, LONG_DISTANCE_RESPONSE and HIERARCHICAL_RELATION separate. Job 3:2 is the negative control.',prohibited='Formal CSF automatically answers previous speaker; semantic response automatically determines hierarchy.')}


def registry():
    b='BOUNDARY_EXISTENCE';f='STRUCTURAL_FUNCTION';l='SAME_LEVEL_RELATION';p='PARENTAGE_CONTAINMENT';c='CLOSURE_TARGET';o='OVERLAY_RESPONSIO';r='RESPONSE_RELATION'
    positive=[
      ('E-EXPLICIT-ONSET','Explicit surface onset construction',[b,f],'HSA013'),
      ('E-EXPLICIT-CLOSURE','Explicit surface closing construction',[b,f,c],'HSA2-F-01'),
      ('E-FORMULA-CORRESPONDENCE','Observable correspondence between formulas',[b,f,l,o,r],'HSA015;HSA016'),
      ('E-FUNCTIONAL-EQUIVALENCE','Separately established structural functions agree',[l],'HSA020;HSA021'),
      ('E-GRAMMATICAL-DEPENDENCY','Explicit grammatical dependency, with its source and scope',[f,p],'HSA013;HSA014'),
      ('E-ENCLOSING-SCOPE','Independently established enclosing scope; not nearest onset',[p,c],'HSA026;HSA2-F-03'),
      ('E-PARTICIPANT-ALIGNMENT','Explicit participant evidence, unresolved references preserved',[b,f,o,r],'HSA025'),
      ('E-ADDRESSEE-ALIGNMENT','Explicit object/addressee correspondence',[o,r],'HSA025'),
      ('E-TIME-FRAME','Surface time-frame change',[b,f],'HSA002'),
      ('E-PLACE-FRAME','Surface place-frame change',[b,f],'HSA002'),
      ('E-LEXICAL-RECURRENCE','Same verified lexical identity recurs',[o,r],'HSA014 (negative control)'),
      ('E-LEXICAL-FAMILY','Supported family relationship; root ambiguity retained',[o,r],'ANA.0.2 32:3/5 (not an adjudication)'),
      ('E-POLARITY-CONTRAST','Positive/negative/cessative polarity contrasted',[o,r],'ANA-C3 (unadjudicated)'),
      ('E-DISTRIBUTIONAL-PATTERN','Unweighted distribution and intervening contexts',[b,l,o,r],'HSA020;HSA021;HSA022;HSA023'),
      ('E-NEGATIVE-CONTROL','Counterexample or continuation evidence constraining a claim',list(DIMENSIONS),'HSA014;HSA2-NO-28;HSA031'),
      ('E-BHSA-CORROBORATION','Syntactic annotation corroboration kept separate from discovery',[f,p,c],'HSA026 (illustrative protocol, not asserted historical rationale)')]
    negative=[('N-ADJACENCY-ONLY','Adjacency without independent relation evidence'),('N-CHAPTER-BOUNDARY-ONLY','Chapter numbering alone'),
      ('N-THEME-ONLY','Thematic similarity/change alone'),('N-SPEAKER-ONLY','Same speaker or alternation alone'),
      ('N-LEXEME-ONLY','Same spelling/root/lexeme alone'),('N-FORMULA-LENGTH-ONLY','Longer formula alone'),
      ('N-NEAREST-OPENING','Nearest opening as an inferred parent'),('N-SEMANTIC-SIMILARITY-ONLY','Semantic response/similarity alone')]
    out=[]
    for code,desc,allowed,example in positive:
        out.append(dict(evidence_code=code,evidence_dimension=allowed,description=desc,admissible_for=allowed,
            insufficient_for=[d for d in DIMENSIONS if d not in allowed],can_support_boundary=b in allowed,can_support_same_level=l in allowed,
            can_support_parentage=p in allowed,can_support_overlay=o in allowed,needs_human_interpretation=True,
            example_existing_judgment=example,methodological_note='Admissible contribution only, never a sufficient automatic decision. Examples are illustrative crosswalks, not retroactive claims about researcher reasoning.',status='DRAFT',sole_basis_sufficient=False))
    for code,desc in negative:
        out.append(dict(evidence_code=code,evidence_dimension=list(DIMENSIONS),description=desc,admissible_for=[],insufficient_for=list(DIMENSIONS),
            can_support_boundary=False,can_support_same_level=False,can_support_parentage=False,can_support_overlay=False,
            needs_human_interpretation=True,example_existing_judgment='HSA014;HSA024;HSA026',
            methodological_note='Forbidden as sole basis. Relevant observations can be retained as context with independent evidence.',status='DRAFT',sole_basis_sufficient=False))
    return out


def document(rows=None):
    rows=registry() if rows is None else rows
    lines=['# HSA Adjudication Criteria Registry — DRAFT','','This registry does not adjudicate any case. No numerical weights, global evidence ranking, scoring or automatic structural rules are defined. Support flags mean admissibility for a relation question, not sufficiency.','',
      'MILAL does not claim to be structure-free. Marker selection is linguistically and theoretically informed, but the final hierarchical outcome is not predetermined. Surface-marker extraction and structural adjudication remain distinct stages.',
      'The same marker does not automatically produce the same structural relation. Evidence can have different relevance to boundary, function, same-level, parentage, closure, overlay and response questions. Equal formulas do not imply equal levels; longer formulas do not imply higher levels.','',
      '## BHSA and MILAL','',
      'BHSA clause/clause_atom syntactic hierarchy is not MILAL discourse/literary hierarchy. BHSA morphology, phrase and clause data are primary linguistic evidence. BHSA mother/tab/pargr/rela/code belong to a validation/corroboration layer separate from discovery; no syntactic mother is converted into a literary parent. MILAL uses clause_atom anchors while cross-chapter discourse hierarchy requires separate adjudication.',
      'This addendum uses lexical/morphological and explicit phrase evidence for discovery. The frozen 0.1 syntactic observations remain historical inputs; their mother links are never promoted to MILAL parentage. No new tab/pargr extraction is claimed.','',
      'LEXICAL COGNATE ≠ SEMANTIC NEIGHBOR ≠ DISCOURSE FUNCTION ≠ HIERARCHICAL RELATION.','']
    for key,p in DIMENSIONS.items():lines += ['## '+key,'',p['question'],'','Admissible evidence: '+p['evidence'],'','Insufficient or forbidden sole basis: '+p['prohibited'],'']
    lines += ['## Evidence codes','', '| Code | Description | Admissible dimensions |','| --- | --- | --- |']
    for row in rows:lines.append('| '+row['evidence_code']+' | '+row['description']+' | '+(', '.join(row['admissible_for']) or 'NONE as sole basis')+' |')
    lines += ['', '## Frozen examples and review discipline','',
      'The existing-judgment crosswalk preserves exact original records, source locators and hashes. Its code assignments are draft illustrative mappings, not new human judgments and not claims that an unstated historical rationale was used. Original linguistic_basis and methodological_note remain visible alongside the mapping.',
      'At Job 31:40 retain DIRECT_LOCAL_CLOSURE to 29:1, NO_DIRECT_RELATION to 27:1 in the direct-closure dimension, and TERMINATES_ENCLOSING_GROUP for POST_DIALOGUE_JOB. At 3:2 a formal CSF does not supply a semantic-response antecedent.',
      'Reviewers must identify the dimension, cite exact source evidence, inspect negative controls and alternatives, and provide a source-supported relation or preserve UNRESOLVED / INSUFFICIENT_EVIDENCE. Q2–Q5 and HSA3 A–G remain unreviewed. R4.4 is not started.','']
    return '\n'.join(lines)
