import copy
import sys
import tempfile
import types
import unittest
from pathlib import Path

from aurora.aneug_cycle_functional_p0 import (
    AneuGCycleP0Error,
    cycle_moments,
    inspect_payloads,
    load_config,
    safe_torch_load,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_cycle_functional_p0.json"


class AneuGCycleFunctionalP0Tests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import torch
        except ImportError:
            torch = None
        self.torch = torch

    def test_frozen_config_is_valid(self) -> None:
        payload = load_config(CONFIG)
        self.assertEqual(payload["candidate"]["source_shortlist_score"], 33)
        self.assertFalse(payload["execution"]["gpu_requested"])
        self.assertEqual(payload["execution"]["server"], "introai9")

    def test_config_rejects_method_or_same_contract_rerun(self) -> None:
        payload = load_config(CONFIG)
        candidate = copy.deepcopy(payload)
        candidate["candidate"]["method_selected"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            import json

            path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaisesRegex(AneuGCycleP0Error, "cannot select a method"):
                load_config(path)

        candidate = copy.deepcopy(payload)
        candidate["execution"]["same_contract_rerun_allowed"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            import json

            path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaisesRegex(AneuGCycleP0Error, "reruns are prohibited"):
                load_config(path)

    def _payloads(self, case_count: int = 3):
        if self.torch is None:
            self.skipTest("PyTorch is unavailable")
        torch = self.torch
        labels = [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
            "wss",
        ]
        registered = []
        names = []
        for case_id in range(case_count):
            name = f"case_{case_id}"
            names.append(name)
            tensor = torch.zeros(80, 4, len(labels), dtype=torch.float32)
            tensor[..., 0] = torch.tensor([0.0, 1.0, 0.0, 0.0]) + case_id
            tensor[..., 1] = torch.tensor([0.0, 0.0, 1.0, 0.0])
            tensor[..., 2] = torch.tensor([0.0, 0.0, 0.0, 1.0])
            tensor[..., 3] = 1.0
            tensor[..., 6] = torch.linspace(-1.0, 1.0, 80).view(80, 1)
            tensor[..., 7] = 0.5
            registered.append({"case": name, "labels": labels, "tensor": tensor})
        steady = {
            "label": labels[:-1],
            "tensor_norm": {
                "mean": torch.zeros(1, 1, len(labels) - 1),
                "std": torch.ones(1, 1, len(labels) - 1),
            },
        }
        transient = {
            "registered_data_list": registered,
            "mesh_data": {
                "cases": names,
                "faces_list": [torch.tensor([[0, 1, 2], [0, 2, 3]])],
            },
        }
        return steady, transient

    def test_payload_contract_and_deidentified_summary(self) -> None:
        steady, transient = self._payloads()
        summary = inspect_payloads(
            steady,
            transient,
            self.torch,
            minimum_cases=3,
            expected_timesteps=80,
            static_tolerance=1e-6,
            roundtrip_tolerance=1e-5,
        )
        self.assertEqual(summary["case_count"], 3)
        self.assertEqual(summary["unique_geometry_count"], 3)
        self.assertFalse(summary["case_identifiers_in_result"])
        self.assertNotIn("case_0", str(summary))

    def test_static_geometry_change_fails(self) -> None:
        steady, transient = self._payloads()
        transient["registered_data_list"][0]["tensor"][1, 0, 0] += 1e-3
        with self.assertRaisesRegex(AneuGCycleP0Error, "Geometry changes"):
            inspect_payloads(
                steady,
                transient,
                self.torch,
                minimum_cases=3,
                expected_timesteps=80,
                static_tolerance=1e-6,
                roundtrip_tolerance=1e-5,
            )

    def test_cycle_moments_exact_identity(self) -> None:
        if self.torch is None:
            self.skipTest("PyTorch is unavailable")
        torch = self.torch
        wss = torch.tensor([[[1.0, 0.0, 0.0]], [[-1.0, 0.0, 0.0]]])
        metrics = cycle_moments(wss, torch)
        self.assertAlmostEqual(float(metrics["tawss"].item()), 1.0)
        self.assertAlmostEqual(float(metrics["osi"].item()), 0.5)
        self.assertGreater(float(metrics["rrt"].item()), 1e10)

    def test_weights_only_reader_loads_plain_tensor_archive(self) -> None:
        if self.torch is None:
            self.skipTest("PyTorch is unavailable")
        torch = self.torch
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plain.pth"
            torch.save({"tensor": torch.arange(4)}, path)
            loaded = safe_torch_load(path, torch)
        self.assertTrue(torch.equal(loaded["tensor"], torch.arange(4)))

    def test_weights_only_reader_allows_only_meshes_state_container(self) -> None:
        if self.torch is None:
            self.skipTest("PyTorch is unavailable")
        torch = self.torch
        module_names = (
            "pytorch3d",
            "pytorch3d.structures",
            "pytorch3d.structures.meshes",
        )
        previous = {name: sys.modules.get(name) for name in module_names}
        root = types.ModuleType("pytorch3d")
        structures = types.ModuleType("pytorch3d.structures")
        meshes = types.ModuleType("pytorch3d.structures.meshes")
        Meshes = type("Meshes", (), {})
        Meshes.__module__ = "pytorch3d.structures.meshes"
        meshes.Meshes = Meshes
        structures.Meshes = Meshes
        structures.meshes = meshes
        root.structures = structures
        sys.modules["pytorch3d"] = root
        sys.modules["pytorch3d.structures"] = structures
        sys.modules["pytorch3d.structures.meshes"] = meshes
        try:
            state = Meshes()
            state.faces = torch.tensor([[0, 1, 2]])
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "meshes.pth"
                torch.save({"mesh": state}, path)
                for name in reversed(module_names):
                    sys.modules.pop(name, None)
                loaded = safe_torch_load(path, torch)
        finally:
            for name in reversed(module_names):
                prior = previous[name]
                if prior is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = prior
        self.assertTrue(torch.equal(loaded["mesh"].faces, torch.tensor([[0, 1, 2]])))


if __name__ == "__main__":
    unittest.main()
