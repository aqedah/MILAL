# Tests

Run `python -m unittest discover -s tests -v` from the repository root.
`test_r3c_0_2.py` exercises synthetic success/failure contracts without BHSA,
including negative tests for all four extension-separation invariants.
Also run `python src/milal_r3c_0_2_reviewability.py --self-test`.

The optional checked-in Job regression checks S02135 evidence from R3c.0.1.
This does not substitute for the real R3c.0.2 Termux/BHSA run and packet review.
