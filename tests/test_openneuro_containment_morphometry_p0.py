from __future__ import annotations

import copy
import hashlib
import json
import pickle
import unittest
from pathlib import Path
from unittest import mock

from aurora.openneuro_containment_morphometry_p0 import (
    OpenNeuroContainmentP0Error,
    load_config,
    run_p0,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "openneuro_containment_morphometry_p0.json"


def _session(subject: str, date: str) -> str:
    return f"{subject}_ses-{date}"


def _synthetic_objects(config: dict) -> dict[str, bytes]:
    code_only = {"sub-115", "sub-143", "sub-181", "sub-272"}
    public_weak = [
        f"sub-{index:03d}"
        for index in range(250)
        if f"sub-{index:03d}" not in code_only and index != 249
    ]
    assert len(public_weak) == 246
    precise = [f"sub-{index:03d}" for index in range(450, 488)]
    weak = public_weak + sorted(code_only)
    assert len(weak) == 250

    precise_sessions = [_session(subject, "20100101") for subject in precise]
    weak_sessions = [_session(subject, "20100101") for subject in weak]
    weak_sessions.extend(_session(subject, "20100102") for subject in public_weak[:12])
    assert len(weak_sessions) == 262

    public = public_weak + precise
    manual_pairs = []
    for index, subject in enumerate(public):
        date = "20100101" if index < 11 else "20110101"
        manual_pairs.append(_session(subject, date))
    manual_pairs.extend(_session(subject, "20120101") for subject in public[:12])
    assert len(manual_pairs) == 296

    paths = []
    for pair in manual_pairs:
        subject, session = pair.split("_", maxsplit=1)
        paths.append(
            f"derivatives/manual_masks/{subject}/{session}/{subject}_{session}_desc-brain_mask.nii.gz"
        )
    for pair in manual_pairs[:198]:
        subject, session = pair.split("_", maxsplit=1)
        paths.append(
            f"derivatives/manual_masks/{subject}/{session}/{subject}_{session}_desc-Lesion_1_mask.nii.gz"
        )
    for subject in public:
        paths.append(f"{subject}/ses-20110101/anat/{subject}_angio.json")
    paths.extend(
        f"metadata/filler_{index:04d}.txt"
        for index in range(5737 - len(paths))
    )
    assert len(paths) == 5737

    objects = {
        "dataset_tree_json": json.dumps(
            {"sha": config["sources"]["dataset_commit"], "truncated": False,
             "tree": [{"path": path, "type": "blob"} for path in paths]}
        ).encode(),
        "dataset_description_json": json.dumps(
            {"License": "CC0", "DatasetDOI": "doi:10.18112/openneuro.ds003949.v1.0.1"}
        ).encode(),
        "precise_subject_list_pickle_bytes_opcode_only": pickle.dumps(
            precise_sessions, protocol=4
        ),
        "weak_subject_list_pickle_bytes_opcode_only": pickle.dumps(
            weak_sessions, protocol=4
        ),
        "code_license_text": b"Apache License\nVersion 2.0, January 2004\n",
    }
    sources = config["sources"]
    sources["dataset_description_sha256"] = hashlib.sha256(
        objects["dataset_description_json"]
    ).hexdigest()
    sources["precise_list_sha256"] = hashlib.sha256(
        objects["precise_subject_list_pickle_bytes_opcode_only"]
    ).hexdigest()
    sources["weak_list_sha256"] = hashlib.sha256(
        objects["weak_subject_list_pickle_bytes_opcode_only"]
    ).hexdigest()
    sources["code_license_sha256"] = hashlib.sha256(
        objects["code_license_text"]
    ).hexdigest()
    return objects


class OpenNeuroContainmentP0ContractTests(unittest.TestCase):
    def test_reference_contract_is_cpu_only_one_shot_on_introai9(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["candidate"]["score"], 32.5)
        self.assertFalse(config["candidate"]["coarsening_mechanism_estimated"])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertEqual(config["execution"]["maximum_submissions_for_exact_public_source"], 1)
        self.assertFalse(config["access"]["patient_nifti_image_or_mask_body_access"])
        self.assertFalse(config["access"]["pickle_unpickling_or_execution"])

    def test_score_source_or_gpu_mutation_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text())
        payload["candidate"]["score"] = 33.0
        payload["execution"]["ngpus"] = 1
        payload["sources"]["dataset_commit"] = "f" * 40
        with self.assertRaises(OpenNeuroContainmentP0Error):
            validate_config(payload)

    def test_pbs_wrapper_forbids_dirty_or_repeated_source_and_gpu(self) -> None:
        script = (ROOT / "cluster" / "pbs_openneuro_containment_morphometry_p0.pbs").read_text()
        self.assertIn("ngpus=0", script)
        self.assertIn("status --porcelain", script)
        self.assertIn("resubmission is forbidden", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("junjinyong", script)


class OpenNeuroContainmentP0ExecutionTests(unittest.TestCase):
    def test_synthetic_exact_metadata_passes_without_patient_payload_or_model(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["_config_sha256"] = "synthetic"
        objects = _synthetic_objects(config)
        with mock.patch(
            "aurora.openneuro_containment_morphometry_p0._fetch_registered_objects",
            return_value=objects,
        ):
            result = run_p0(config, public_source_commit="a" * 40)
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["counts"]["public_weak_subjects"], 246)
        self.assertEqual(result["counts"]["public_precise_subjects"], 38)
        self.assertEqual(result["counts"]["code_session_pairs_matching_public_tree"], 11)
        self.assertFalse(result["access"]["pickle_unpickled_or_executed"])
        self.assertFalse(result["access"]["patient_nifti_image_or_mask_body"])
        self.assertFalse(result["authorization"]["method"])
        self.assertFalse(result["authorization"]["gpu"])

    def test_tree_response_must_match_the_registered_dataset_commit(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["_config_sha256"] = "synthetic"
        objects = _synthetic_objects(config)
        tree = json.loads(objects["dataset_tree_json"])
        tree["sha"] = "f" * 40
        objects["dataset_tree_json"] = json.dumps(tree).encode()
        with mock.patch(
            "aurora.openneuro_containment_morphometry_p0._fetch_registered_objects",
            return_value=objects,
        ):
            result = run_p0(config, public_source_commit="c" * 40)
        self.assertFalse(result["gate_passed"])
        self.assertFalse(result["checks"]["exact_commits_and_small_blob_hashes"])

    def test_unmapped_public_subject_fails_all_or_none_gate(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["_config_sha256"] = "synthetic"
        objects = _synthetic_objects(config)
        tree = json.loads(objects["dataset_tree_json"])
        tree["tree"].append(
            {"path": "sub-900/ses-20110101/anat/sub-900_angio.json", "type": "blob"}
        )
        objects["dataset_tree_json"] = json.dumps(tree).encode()
        with mock.patch(
            "aurora.openneuro_containment_morphometry_p0._fetch_registered_objects",
            return_value=objects,
        ):
            result = run_p0(config, public_source_commit="b" * 40)
        self.assertFalse(result["gate_passed"])
        self.assertFalse(
            result["checks"]["public_subjects_partition_exactly_into_246_weak_and_38_precise"]
        )


if __name__ == "__main__":
    unittest.main()
