from __future__ import annotations

import unittest

from system import evaluate_scores, popularity_scores, score_rows, smoke_result
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


if __name__ == "__main__":
    unittest.main()
