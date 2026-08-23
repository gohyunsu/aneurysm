import hashlib
import unittest

import torch

from aurora.aneug_release_730_matched_steady_stream import (
    ExposureDigest,
    MatchedSteadyStream,
    MatchedSteadyStreamError,
    epoch_exposure_indices,
    single_field_relative_squared_error,
)
from aurora.aneug_release_730_steady_exposure_schedule import exposure_prefix


class TrackingRows:
    def __init__(self, value):
        self.value = value
        self.shape = value.shape
        self.indices = []

    def __getitem__(self, index):
        self.indices.append(index)
        return self.value[index]


def synthetic_archive(rows=5, nodes=4):
    tensor = torch.zeros(rows, nodes, 9)
    base = torch.tensor(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    )
    tensor[:, :, :3] = base
    tensor[:, :, 5] = 1.0
    for row in range(rows):
        tensor[row, :, 6:] = float(row + 1)
    ghd = torch.arange(rows * 432, dtype=torch.float32).reshape(rows, 432)
    tracked_tensor = TrackingRows(tensor)
    tracked_ghd = TrackingRows(ghd)
    archive = {
        "label": [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ],
        "tensor_norm": {"mean": torch.zeros(9), "std": torch.ones(9)},
        "tensor": tracked_tensor,
        "ghd_dict": {"ghd": tracked_ghd},
        "case_name": [f"case-{index}" for index in range(rows)],
    }
    faces = torch.tensor([[0, 1, 2], [0, 2, 3]])
    return archive, tracked_tensor, tracked_ghd, faces


def synthetic_stream(archive, faces):
    eligible = [0, 2, 4]
    digest = hashlib.sha256("0\n2\n4".encode("utf-8")).hexdigest()
    case_digest = hashlib.sha256(
        "case-0\ncase-2\ncase-4".encode("utf-8")
    ).hexdigest()
    return MatchedSteadyStream(
        archive,
        eligible,
        ghd_mean=torch.zeros(432),
        ghd_std=torch.ones(432),
        faces=faces,
        expected_rows=5,
        expected_nodes=4,
        expected_eligible_rows=3,
        expected_ordered_index_digest=digest,
        expected_ordered_case_digest=case_digest,
    )


class MatchedSteadyStreamTests(unittest.TestCase):
    def test_epoch_generator_matches_registered_prefix_without_full_materialization(self):
        eligible = tuple(range(17))
        actual = []
        for epoch in range(6):
            actual.extend(
                epoch_exposure_indices(
                    eligible, epoch=epoch, cases_per_epoch=5, seed=20260821
                )
            )
        expected = exposure_prefix(
            eligible, epochs=6, cases_per_epoch=5, seed=20260821
        )
        self.assertEqual(tuple(actual), expected)

    def test_incremental_digest_matches_newline_joined_schedule_digest(self):
        values = tuple(range(11, 39, 3))
        ledger = ExposureDigest()
        for value in values:
            ledger.update(value)
        expected = hashlib.sha256(
            "\n".join(str(value) for value in values).encode("utf-8")
        ).hexdigest()
        self.assertEqual(ledger.count, len(values))
        self.assertEqual(ledger.hexdigest(), expected)

    def test_constructor_reads_metadata_only_and_decode_indexes_one_row(self):
        archive, tensor, ghd, faces = synthetic_archive()
        stream = synthetic_stream(archive, faces)
        self.assertEqual(tensor.indices, [])
        self.assertEqual(ghd.indices, [])
        case = stream.decode(2)
        self.assertEqual(tensor.indices, [2])
        self.assertEqual(ghd.indices, [2])
        self.assertEqual(tuple(case["coordinates"].shape), (4, 3))
        self.assertEqual(tuple(case["steady_wss"].shape), (4, 3))
        self.assertAlmostEqual(float(case["vertex_weights"].sum()), 1.0, places=6)
        self.assertTrue(torch.isfinite(case["normals"]).all())
        self.assertTrue(torch.isfinite(case["ghd"]).all())

    def test_ineligible_row_is_rejected_before_archive_indexing(self):
        archive, tensor, ghd, faces = synthetic_archive()
        stream = synthetic_stream(archive, faces)
        with self.assertRaisesRegex(MatchedSteadyStreamError, "ineligible_row"):
            stream.decode(1)
        self.assertEqual(tensor.indices, [])
        self.assertEqual(ghd.indices, [])

    def test_wrong_eligible_digest_is_rejected_without_field_indexing(self):
        archive, tensor, ghd, faces = synthetic_archive()
        with self.assertRaisesRegex(
            MatchedSteadyStreamError, "eligible_index_digest"
        ):
            MatchedSteadyStream(
                archive,
                [0, 2, 4],
                ghd_mean=torch.zeros(432),
                ghd_std=torch.ones(432),
                faces=faces,
                expected_rows=5,
                expected_nodes=4,
                expected_eligible_rows=3,
                expected_ordered_index_digest="0" * 64,
                expected_ordered_case_digest="0" * 64,
            )
        self.assertEqual(tensor.indices, [])
        self.assertEqual(ghd.indices, [])

    def test_archive_case_order_drift_is_rejected_without_field_indexing(self):
        archive, tensor, ghd, faces = synthetic_archive()
        archive["case_name"][0], archive["case_name"][2] = (
            archive["case_name"][2],
            archive["case_name"][0],
        )
        with self.assertRaisesRegex(
            MatchedSteadyStreamError, "eligible_case_order_digest"
        ):
            synthetic_stream(archive, faces)
        self.assertEqual(tensor.indices, [])
        self.assertEqual(ghd.indices, [])

    def test_single_field_loss_has_correct_area_weighting(self):
        reference = torch.tensor([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        prediction = torch.tensor([[2.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        weights = torch.tensor([0.25, 0.75])
        loss = single_field_relative_squared_error(prediction, reference, weights)
        expected = (0.25 * 1.0 + 0.75 * 1.0) / (0.25 * 1.0 + 0.75 * 4.0)
        self.assertAlmostEqual(float(loss), expected, places=7)


if __name__ == "__main__":
    unittest.main()
