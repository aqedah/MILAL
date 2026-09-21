# Fabricated MR1 regression fixture

Five synthetic clauses and six atoms, constructed in `milal_mr1_synthetic.sample`.
These four small CSVs are generated once from the isolated historical dependency
closure and checked in as regression snapshots, **not** independent historical
ground truth or a recovered empirical run. Rule tests independently assert the
intended source behavior and mutate its boundary conditions.

Expected facts inspected at creation: clause 10000 Way0/HYH 3ms with Time phrase
and two atoms; clause 10001 SIMPLE_AMR with Job subject and Eliphaz explicit
addressee, profile EXPANDED but scope CORE; clause 10002 Q content; clause 10003
one-clause תמם+דבר closure; clause 10004 a negative Way0 audit candidate. Exactly
5 surface, 1 CSF, 1 closure, 2 Way0 rows (1 positive, 1 negative), 9 event/clause
linkage rows. Fixture values and IDs do not occur as detection controls.

The scoped `.gitattributes` exception checks out these four fixtures as UTF-8
BOM / CRLF (Git stores normalized text), making byte regression portable.
