bottlenecks:

  - id: B001

    description: >
      Click-conditioned CVR training appears to create a sample-selection
      bottleneck: the model learns conversion only from clicked impressions and
      may therefore generalize poorly to the population used by the task.

    opened_by_evidence: D001

    formation:

      observed_symptom: >
        On S001, CVR AUC is 0.5912 while CTR AUC is 0.6210. The baseline CVR
        learner is trained only on clicked samples, so its training population
        is substantially narrower than the impression population available to
        the joint task.

      mechanism_analysis: >
        Conditioning CVR learning on clicks can create sample-selection bias:
        features associated with whether an impression is clicked also affect
        which examples are visible to the CVR learner. Entire-space supervision
        should help specifically if this missing population coverage is an
        important mechanism. The score gap alone does not establish causality.

      diagnostic_experiments:

        - id: D001

          starting_state: S001

          question: >
            Is the weak CVR result associated with clicked-only population
            coverage rather than simply a generally weak model?

          protocol: >
            On a fixed 10% train-only proxy and seed 0, compare the baseline's
            clicked-only CVR training population with the full impression
            population used by CTR. Measure coverage and feature-distribution
            differences without changing the model or evaluator. Stop after the
            preregistered population and slice diagnostics.

          expected_result: >
            If selection bias is plausible, clicked samples should cover a
            materially shifted and narrower population than all impressions.
            If the populations are nearly identical on the relevant features,
            this mechanism becomes substantially less plausible.

          actual_result: >
            Clicked samples were materially shifted on several high-volume
            categorical slices and represented only a subset of the impression
            population used by CTR. The diagnostic established a real coverage
            difference but did not show that it caused the CVR score gap.

          interpretation: >
            D001 makes sample selection an actionable bottleneck candidate and
            motivates a controlled entire-space intervention. It does not rule
            out capacity, optimization, or multi-task regularization effects.

          result_audit: >
            The diagnostic used only training data and fixed slices. No hidden
            test data or validation-specific selection was used. Because this
            is a distribution diagnostic, it cannot by itself establish the
            causal effect on CVR AUC.

          log: research_record/logs/D001.log

          resources:
            llm_tokens: null
            llm_tokens_scope: scientist_session
            llm_accounting_status: unavailable
            gpu_hours: 0.0
            wall_time_hours: 0.05

          resulting_state: null

      competing_explanations:

        - id: C001

          explanation: >
            The CVR model is simply under-capacity or poorly optimized, and the
            clicked-only population is not the dominant limiting mechanism.

          evidence_for: >
            S001 uses a simple independent MLP-style formulation, so model
            capacity and optimization remain plausible contributors.

          evidence_against: >
            D001 shows a substantial population shift specific to the CVR
            training setup that capacity alone does not explain.

          status: unresolved

        - id: C002

          explanation: >
            The apparent weakness is primarily an evaluator or split artifact.

          evidence_for: >
            The current evidence is still medium fidelity and should not be
            treated as a final benchmark claim.

          evidence_against: >
            The same fixed evaluator and split are used for both baseline and
            planned controls, and D001 is based on train-only population facts.

          status: deprioritized

      selection_rationale: >
        D001 identifies a concrete population-coverage mechanism that is
        specific to the current CVR formulation and can be tested by an
        entire-space intervention while keeping the evaluator fixed. Capacity
        remains a competing explanation and must be considered in the result
        audit.

      falsifiers: >
        If an entire-space intervention leaves CVR unchanged under a fair
        control, or if a capacity-matched clicked-only model explains the same
        gains, the sample-selection bottleneck should be weakened or redefined.

    status: active
    closed_by_evidence: null
    archive: null
    closure: null

    hypotheses:

      - id: H001

        description: >
          Sample selection is an important contributor to weak CVR performance;
          using entire-space CTR and CTCVR supervision should improve CVR more
          than a comparable clicked-only formulation.

        experiments:

          - id: E001

            starting_state: S001

            protocol: >
              On the fixed 10% train-only proxy, seed 0, replace the independent
              clicked-only CVR head with ESMM while keeping the loader, split,
              evaluator, optimizer budget, and stopping rule fixed. Run at
              medium fidelity and stop after the preregistered training budget.

            expected_result: >
              If sample selection is important, CVR AUC should improve
              noticeably more than CTR AUC. If both metrics stay effectively
              unchanged, H001 receives little support.

            actual_result: >
              On the same development setup, the ESMM version increased CVR AUC
              from 0.5912 to 0.5960 while CTR AUC increased from 0.6210 to
              0.6217. The experiment used a 10% proxy dataset and one random
              seed.

            evaluation:

              status: completed
              fidelity: medium
              split: train_holdout

              primary_metric:
                name: CVR_AUC
                value: 0.5960

              metrics:
                CVR_AUC: 0.5960
                CTR_AUC: 0.6217

              compared_with_state: S001
              improvement_over_comparator: 0.0048

            events: >
              The first training run crashed with out-of-memory; recovered by
              halving the batch size and rerunning. No other incidents.

            log: research_record/logs/E001.log

            resources:
              llm_tokens: 48230
              llm_tokens_scope: meta_scientist_cycle
              llm_accounting_status: measured
              gpu_hours: 0.4

            result_audit: >
              The direction matches the preregistered expectation and no
              evaluator or data-split modifications were made. However, ESMM
              changes both population supervision and architecture, so
              multi-task regularization or capacity can still explain part of
              the gain. One seed and a 10% proxy also limit confidence.

            conclusion: >
              E001 provides provisional support for H001 and justifies further
              work inside B001, but it does not yet establish sample selection
              as the unique causal explanation.

            resulting_state: S002

manual_interventions: []

  # - at: E001
  #   what: manually restarted the GPU driver after it hung mid-training
