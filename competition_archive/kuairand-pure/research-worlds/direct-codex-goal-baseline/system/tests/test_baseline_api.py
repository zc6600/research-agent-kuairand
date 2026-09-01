from __future__ import annotations

import math
import unittest

from system import (
    evaluate_scores,
    fm_pairwise_scores,
    fm_scores,
    popularity_scores,
    score_rows,
    score_rows_fm,
    score_rows_fm_pairwise,
    smoke_result,
)
from system.baseline_api import smoke_rows


class BaselineApiTests(unittest.TestCase):
    def test_smoke_result_uses_official_metric_shape(self) -> None:
        result = smoke_result()
        self.assertEqual(result["users"], 2)
        self.assertEqual(result["rows"], 4)
        self.assertIn("GAUC", result)
        self.assertIn("nDCG@5", result)
        self.assertIn("primary", result)
        self.assertGreaterEqual(result["primary"], 0.0)

    def test_popularity_scores_are_submission_compatible(self) -> None:
        splits = smoke_rows()
        records = score_rows(splits["train"], splits["valid"], prior=1.0)
        self.assertEqual([record["row_id"] for record in records], [0, 1, 2, 3])
        self.assertEqual(records[0]["user_id"], "u1")
        self.assertEqual(records[0]["video_id"], "v1")
        self.assertIsInstance(records[0]["score"], float)

    def test_evaluate_scores_accepts_api_scores(self) -> None:
        splits = smoke_rows()
        scores = popularity_scores(splits["train"], splits["valid"], prior=1.0)
        result = evaluate_scores(splits["valid"], scores)
        self.assertEqual(result, smoke_result())

    def test_fm_scores_are_deterministic_and_submission_compatible(self) -> None:
        splits = smoke_rows()
        first = fm_scores(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=3,
            batch_size=2,
            seed=7,
        )
        second = fm_scores(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=3,
            batch_size=2,
            seed=7,
        )
        self.assertEqual(len(first), len(splits["valid"]))
        self.assertEqual(first, second)
        self.assertTrue(all(math.isfinite(first_score) for first_score in first))

        records = score_rows_fm(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=1,
            batch_size=2,
        )
        self.assertEqual([record["row_id"] for record in records], [0, 1, 2, 3])

    def test_pairwise_fm_is_deterministic_and_submission_compatible(self) -> None:
        splits = smoke_rows()
        first = fm_pairwise_scores(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=3,
            batch_size=2,
            seed=7,
        )
        second = fm_pairwise_scores(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=3,
            batch_size=2,
            seed=7,
        )
        self.assertEqual(first, second)
        self.assertTrue(all(math.isfinite(score) for score in first))
        records = score_rows_fm_pairwise(
            splits["train"],
            splits["valid"],
            validation_rows=splits["valid"],
            epochs=1,
            batch_size=2,
            negatives_per_positive=2,
            extra_fields=("user_tab",),
        )
        self.assertEqual([record["row_id"] for record in records], [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()
