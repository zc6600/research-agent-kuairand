experiments:

  - id: E001

    record: >
      Hypothesis-driven experiment. The current pointwise objective may be
      misaligned with the within-user ranking evaluator, so replacing pointwise
      BCE with pairwise training may improve relative ordering. Starting from
      S001, we kept the same development split and evaluator and trained a
      pairwise FM with k=16, lr=0.001, seed=0. The run produced GAUC 0.670248,
      nDCG@5 0.537268, and primary 0.603758 versus the pointwise FM primary
      0.601469. This supports objective/evaluator mismatch as an important
      explanation for the pointwise baseline's weakness, but it does not show
      that pairwise training is the only remaining source of headroom or that
      the effect is fully robust across seeds.

    primary_metric:
      name: primary
      value: 0.603758

    official_score: true

    resulting_state: S002

    evidence:
      - research_record/logs/E001.log
      - research_record/logs/E001.metrics.json

  - id: E002

    record: >
      Exploratory experiment. We did not have a strong causal hypothesis, but
      wanted to learn whether harder negatives contained useful ranking signal.
      Using the current pairwise FM as the comparator, we changed only negative
      selection and evaluated progressively harder pools in a reduced diagnostic
      setting. The proxy metric degraded sharply as the negatives became harder;
      pool=5 produced 0.533402 while the random-negative control remained around
      0.603874. This is strong evidence that the current hardness rule is not a
      useful training signal in this setup. It does not by itself identify
      whether the failure comes from label ambiguity, exposure bias, model-score
      feedback, or another sampling artifact, and this diagnostic score is not
      part of the official development frontier.

    primary_metric:
      name: diagnostic_primary
      value: 0.533402

    official_score: false

    resulting_state: null

    evidence:
      - research_record/logs/E002.log

manual_interventions: []
