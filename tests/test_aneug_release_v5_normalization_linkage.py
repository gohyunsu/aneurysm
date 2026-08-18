from __future__ import annotations

import copy
import unittest
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None

from aurora.aneug_release_v5_normalization_linkage import compare_loaded, load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_v5_normalization_linkage_v1.json"


class AneuGV5NormalizationLinkageConfigTests(unittest.TestCase):
    def test_config_is_valid(self):
        self.assertEqual(load_config(CONFIG)["expected"]["v4_v5_overlap_count"], 578)


@unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
class AneuGV5NormalizationLinkageTensorTests(unittest.TestCase):
    def test_complete_overlap_is_required(self):
        config = copy.deepcopy(load_config(CONFIG))
        config["expected"]["case_tensor_shape"] = [2, 3, 9]
        labels = config["expected"]["labels"]
        norm = {
            "label": labels,
            "tensor_norm": {
                "mean": torch.zeros(1, 1, 9),
                "std": torch.ones(1, 1, 9),
            },
        }
        shared = [f"case_{index}" for index in range(578)]
        extra = [f"extra_{index}" for index in range(231)]
        tensor = torch.zeros(2, 3, 9)

        def payload(case_ids):
            return {
                "registered_data_list": [
                    {"case": case_id, "labels": labels, "tensor": tensor}
                    for case_id in case_ids
                ],
                "mesh_data": {
                    "cases": case_ids,
                    "ghd": torch.arange(len(case_ids), dtype=torch.float32)[:, None].repeat(1, 432),
                    "idx_list": [torch.tensor([0, 1])],
                    "edge_index_list": [torch.tensor([[0, 1], [1, 0]])],
                    "faces_list": [torch.tensor([[0, 1, 2]])],
                },
            }

        v4 = payload(shared)
        v5 = payload(shared + extra)
        result = compare_loaded(norm, v4, v5, config, torch)
        self.assertEqual(result["tensor_exact_equal_overlap_count"], 578)
        self.assertTrue(result["overlap_identity_supports_common_preprocessing_lineage"])


if __name__ == "__main__":
    unittest.main()
