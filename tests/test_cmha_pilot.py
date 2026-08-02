import unittest

try:
    import numpy as np
    import torch  # noqa: F401

    from aurora.cmha_pilot import classification_metrics, grouped_stratified_folds
except ModuleNotFoundError:
    np = None


@unittest.skipIf(np is None, "CMHA pilot tests require the experiment runtime")
class CMHAPilotTests(unittest.TestCase):
    def test_perfect_predictions_have_unit_ranking_metrics(self) -> None:
        labels = np.asarray([0, 1, 0, 1, 1], dtype=np.int64)
        probabilities = np.asarray([0.05, 0.85, 0.10, 0.70, 0.95])
        metrics = classification_metrics(labels, probabilities)
        self.assertAlmostEqual(metrics["auroc"], 1.0)
        self.assertAlmostEqual(metrics["auprc"], 1.0)
        self.assertAlmostEqual(metrics["balanced_accuracy"], 1.0)

    def test_grouped_folds_never_split_a_patient(self) -> None:
        labels = np.asarray([0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1])
        groups = np.asarray([0, 0, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9])
        folds = grouped_stratified_folds(labels, groups, n_splits=3, seed=7)
        seen: dict[int, int] = {}
        for fold_index, indices in enumerate(folds):
            for group in np.unique(groups[indices]):
                self.assertNotIn(int(group), seen)
                seen[int(group)] = fold_index
        self.assertEqual(set(seen), set(groups))

    def test_grouped_folds_are_reproducible(self) -> None:
        labels = np.asarray([0, 1] * 10)
        groups = np.arange(20)
        first = grouped_stratified_folds(labels, groups, n_splits=5, seed=11)
        second = grouped_stratified_folds(labels, groups, n_splits=5, seed=11)
        for left, right in zip(first, second):
            np.testing.assert_array_equal(left, right)


if __name__ == "__main__":
    unittest.main()
