"""Append-only reconsideration of candidate sets when later evidence arrives."""
import hashlib
from milal_mfr02r_data import encode

STATUSES = ('INITIAL_CANDIDATE', 'PROVISIONAL_RELATION', 'RECONSIDERED_AFTER_LATER_EVIDENCE',
            'REVISED_RELATION', 'RETAINED_RELATION')


class RevisionHistory:
    def __init__(self, sink=None):
        self.rows = []
        self.current = {}
        self.sink = sink
        self.last_hash = ''
        self.count = 0

    def append(self, pair_id, status, original, evidence, trigger, revised, reason):
        if status not in STATUSES:
            raise ValueError('unknown revision state')
        if status in ('REVISED_RELATION', 'RETAINED_RELATION', 'RECONSIDERED_AFTER_LATER_EVIDENCE') and not evidence:
            raise ValueError('revision lacks evidence')
        previous_hash = self.last_hash
        self.count += 1
        row = dict(history_id='RH%09d' % self.count, pair_id=pair_id, status=status,
                   original_relation=list(original), new_evidence=evidence, trigger_clause=trigger,
                   revised_relation=list(revised), revision_reason=reason,
                   revision_scope='CANDIDATE_ALTERNATIVES_ONLY_NOT_HUMAN_JUDGMENT', previous_sha256=previous_hash,
                   generation_stage='MFR.0.2R', engine_version='MFR.0.2R-2', candidate_status=status,
                   human_status='', revision_event=status, evidence_added=evidence, evidence_removed=[], reason=reason)
        row['history_sha256'] = hashlib.sha256(encode(row).encode()).hexdigest()
        self.last_hash = row['history_sha256']
        if self.sink is None:
            self.rows.append(row)
        else:
            self.sink(row)
        self.current[pair_id] = list(revised)
        return row

    def initialize(self, pair_id, relations, trigger, rule_ids):
        self.append(pair_id, 'INITIAL_CANDIDATE', [], rule_ids, trigger, relations, 'Linguistic candidate discovery')
        self.append(pair_id, 'PROVISIONAL_RELATION', relations, rule_ids, trigger, relations, 'No accepted relation assigned')

    def reconsider(self, pair_id, later_evidence, trigger, additional_relations=()):
        original = self.current[pair_id][:]
        self.append(pair_id, 'RECONSIDERED_AFTER_LATER_EVIDENCE', original, later_evidence, trigger, original,
                    'Later source-linked correspondence affects the provisional network')
        revised = sorted(set(original) | set(additional_relations))
        status = 'REVISED_RELATION' if set(revised) != set(original) else 'RETAINED_RELATION'
        self.append(pair_id, status, original, later_evidence, trigger, revised,
                    'Candidate alternatives expanded' if status == 'REVISED_RELATION' else 'Existing alternatives retained; contextual evidence appended')


def verify_history(rows):
    previous = ''
    for row in rows:
        payload = {k: v for k, v in row.items() if k != 'history_sha256'}
        payload['trigger_clause'] = int(payload['trigger_clause'])
        if row['previous_sha256'] != previous or hashlib.sha256(encode(payload).encode()).hexdigest() != row['history_sha256']:
            return False
        previous = row['history_sha256']
    return True


def secondary_semantic_candidate(source_id, target_id, evidence, blind_frozen):
    """Explicit secondary input only; no fabricated semantic model in pass 1."""
    if not blind_frozen:
        raise ValueError('semantic evidence before linguistic freeze')
    if not all(evidence.get(k) for k in ('source_author', 'source_section', 'source_page', 'concept', 'source_node_ids')):
        raise ValueError('semantic evidence lacks provenance')
    return dict(source_clause_id=source_id, target_clause_id=target_id,
                status='SEMANTIC_CORRESPONDENCE_CANDIDATE', role='SECONDARY_CANDIDATE_EVIDENCE',
                evidence=evidence, accepted_mother='', canonical_level='')
