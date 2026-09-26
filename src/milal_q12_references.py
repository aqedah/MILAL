"""Reference evidence without automatic referent adjudication."""
from collections import defaultdict
from milal_q1_binding import identity
from milal_q12_profiles import valid, INDEPENDENT


def morphology(word):
    values=tuple(word.get(k) for k in ('ps','gn','nu'))
    # Nominal person is often NA in BHSA. Preserve that absence; do not invent
    # third person. Gender/number can still supply an unresolved search witness.
    return values if all(valid(v) for v in values[1:]) else None


class ReferenceIndex:
    def __init__(self, configurations):
        self.configurations=configurations;self.witnesses=[];self.antecedents=[]
        self.by_target=defaultdict(list);seen=[]
        for cid in configurations.order:
            row=configurations.rows[cid];p=configurations.profiles[cid]
            forms=list(p['reference_morphology'])
            # Explicit NP recurrence remains a lexical-anaphoric search candidate,
            # never a resolved reference merely because the lexeme repeats.
            for phrase in p['participant_grammatical_roles']:
                for n in phrase['nominals']:
                    if n['sp'] in ('subs','nmpr'):
                        forms.append(dict(node=n['node'],kind='LEXICAL_NP',lex=n['lex'],png=None,identity='UNRESOLVED'))
            forms={identity(f):f for f in forms}
            for form in forms.values():
                png=tuple(form['png']) if form.get('png') and all(valid(x) for x in form['png']) else None
                candidates=[]
                for ant in seen:
                    bases=[]
                    if png and ant['png']:
                        if ant['png']==png:bases.append('PNG_COMPATIBLE_ONLY')
                        elif not valid(ant['png'][0]) and ant['png'][1:]==png[1:]:
                            bases.append('GENDER_NUMBER_COMPATIBLE_PERSON_UNSPECIFIED_ONLY')
                    if form['lex']==ant['lex']:bases.append('LEXICAL_RECURRENCE_ONLY')
                    # Only an exact native word-to-word reference annotation can
                    # license EXACT_NATIVE. Clause attachment is not coreference.
                    exact=[e for e in p['native_annotations'] if int(e['dependent_node'])==int(form['node'])
                        and int(e['head_node'])==ant['word_node'] and e['resolution']=='EXACT_NODE_MEMBERSHIP'
                        and e.get('reference_semantics')=='EXPLICIT_ANTECEDENT']
                    if exact:bases.append('EXACT_NATIVE_WORD_REFERENCE')
                    if bases:candidates.append(dict(**ant,antecedent_basis=bases,native_reference_edges=exact))
                exact=[a for a in candidates if a['native_reference_edges']]
                status=('EXACT_NATIVE' if len(exact)==1 else 'MULTIPLE_PLAUSIBLE' if len(candidates)>1 else
                    'UNIQUE_SURFACE_CANDIDATE' if candidates else 'UNRESOLVED' if not png and form['kind']!='LEXICAL_NP' else 'NO_CANDIDATE')
                record=dict(target_clause_id=cid,target_reference_form=form,person=png[0] if png else '',
                    gender=png[1] if png else '',number=png[2] if png else '',suffix_pronoun_type=form['kind'],
                    explicit_lexical_form=form['lex'],candidate_antecedent_ids=[a['antecedent_id'] for a in candidates],
                    antecedent_basis=sorted({b for a in candidates for b in a['antecedent_basis']}),candidate_count=len(candidates),
                    reference_status=status,referential_identity='EXACT_NATIVE_WORD_REFERENCE' if status=='EXACT_NATIVE' else 'UNRESOLVED',
                    exact_antecedent_id=exact[0]['antecedent_id'] if status=='EXACT_NATIVE' else '',
                    provenance=dict(profile_id=p['profile_id'],source_node=form['node']))
                record['reference_witness_id']='RW-'+identity(record)
                self.witnesses.append(record);self.by_target[cid].append(record)
                for ant in candidates:self.antecedents.append(dict(reference_witness_id=record['reference_witness_id'],**ant))
            current={}
            for phrase in p['participant_grammatical_roles']:
                for n in phrase['nominals']:
                    if n['sp'] in ('subs','nmpr'):
                        current[n['node']]=dict(antecedent_id='ANT-'+str(n['node']),clause_id=cid,word_node=n['node'],
                            phrase_node=phrase['node'],grammatical_role=phrase['function'],lex=n['lex'],png=morphology(n))
            seen.extend(current.values())
        self.candidates=defaultdict(list)
        for a in self.antecedents:self.candidates[a['reference_witness_id']].append(a)

    def bindings(self,source,target):
        source,target=str(source),str(target);results=[]
        for r in self.by_target[target]:
            if r['reference_status']!='EXACT_NATIVE':continue
            antecedent=next(a for a in self.candidates[r['reference_witness_id']] if a['antecedent_id']==r['exact_antecedent_id'])
            mechanism='SB10' if r['suffix_pronoun_type']=='LEXICAL_NP' else 'SB02'
            membership=None
            if antecedent['clause_id']!=source:
                unit=self.configurations.configurations[source]
                if unit['configuration_independence_status'] not in INDEPENDENT:continue
                if antecedent['clause_id'] not in unit['members'] or target in unit['members']:continue
                mechanism='SB03';membership=unit
            results.append(dict(mechanism=mechanism,source_id=source,target_id=target,
                reference_witness=r,antecedent_inside_unit=antecedent,unit_membership_basis=membership,
                source_opening_candidate=source,positive_source_binding=True))
        return results
