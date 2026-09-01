# Cycle-2 E008 evidence snapshot

This is the compact, report-facing evidence record for the separate
`gemini-3.7-flash`-only Research Agent trajectory. The comparison is frozen at
Cycle 2; later experiments in the same local world are not used for the
headline comparison.

## Run boundary

| Field | Recorded value |
|---|---|
| Research world | `research-worlds/gemini-3.7-flash-only-cycle2-e008` |
| Research-agent roles | `gemini-3.7-flash` for META and Scientist |
| Boundary | Cycle 2, experiment `E008_din_dualseq` |
| Model checkpoint | DIN, Seed 42, extended features, BCE loss |
| Resume timing | 2026-09-01 02:00:48 Singapore time; approximately 14 minutes after resume |
| Validation split | KuaiRand-Pure public validation, 124,909 rows |

## Result

| Metric | E008 value | Delta vs official reference |
|---|---:|---:|
| GAUC | **0.6725** | **+0.0051** |
| nDCG@5 | **0.5380** | **+0.0023** |
| Primary = mean(GAUC, nDCG@5) | **0.6052** | **+0.0036** |

The result is accepted here as the Cycle-2 endpoint requested for the
comparison. It is a public-validation search result, not an independent
generalization estimate.

## Token accounting

The comparison axis is total input plus output including cache-read input:

| Boundary | Tokens | Meaning |
|---|---:|---|
| Cycle-1 system cost plus Cycle-2 Scientist | **45,043,916** | Directly attributable cumulative minimum through Cycle 2 |
| Same boundary with unsplittable META aggregate included | **51,173,911** | Conservative upper bound; includes the complete META aggregate spanning Cycles 2–4 |

The interval is an accounting bound, not uncertainty on the score. Its
supporting non-cache interval is 2,070,960–2,898,630. The Cycle-2 Scientist
session itself contributed **802,865** non-cache input + output tokens and
**20,301,989** cache-read input tokens. The exact META slice at the Cycle-2
boundary was not recorded, so the figure uses the interval rather than
inventing a point estimate.

## Protocol qualification

The sequence builder can use earlier validation impressions as online history,
and some other facets use validation labels. E008 uses only the `vid` facet,
so this snapshot does not claim that E008 consumed label-conditioned history.
Whether earlier validation impression IDs are allowed under the organizer's
offline protocol remains unresolved. Accordingly, the evidence level is
**artifact-backed / protocol-qualified**: the score, checkpoint, and token
boundary are recorded, while causal or leakage-free claims remain out of scope.

## Source identity

- Structured trajectory report: [`cycle-2.md`](../research-worlds/gemini-3.7-flash-only-cycle2-e008/research_record/reports/cycle-2.md)
- Supporting experiment log: [`E008_din_dualseq.log`](../research-worlds/gemini-3.7-flash-only-cycle2-e008/research_record/logs/E008_din_dualseq.log)
- SHA-256 of the supporting log: `8a121c67484b835b3c7faa58af717f90dc23f882faf29857c2b04d86b5603c83`

The raw log is retained in the local research-world snapshot for provenance;
this tracked snapshot is the public claim boundary and avoids depending on
ignored child-repository runtime files.
