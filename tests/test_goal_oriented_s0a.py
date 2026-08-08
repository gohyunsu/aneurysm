import copy
import json
import unittest
from pathlib import Path

from aurora.goal_oriented_s0a import (
    S0AProtocolError,
    load_s0a_config,
    validate_s0a_config,
)
from aurora.goal_oriented_s0a_solver import (
    SolverPreflightProtocolError,
    load_solver_preflight_config,
    validate_solver_preflight_config,
)
from aurora.goal_oriented_s0a_staging import (
    StagingProtocolError,
    load_staging_config,
    validate_staging_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "goal_oriented_segmentation_s0a.json"
STAGING_PBS = ROOT / "cluster" / "pbs_goal_oriented_s0a_stage_cmha.pbs"
SOLVER_CONFIG = ROOT / "configs" / "goal_oriented_segmentation_s0a_solver_preflight.json"
SOLVER_PBS = ROOT / "cluster" / "pbs_goal_oriented_s0a_solver_preflight.pbs"
STAGING_V2_CONFIG = ROOT / "configs" / "goal_oriented_segmentation_s0a_cmha_stage_v2.json"
STAGING_V2_PBS = ROOT / "cluster" / "pbs_goal_oriented_s0a_stage_cmha_v2.pbs"
STAGING_V1_RECORD = ROOT / "results" / "goal_oriented_s0a_cmha_stage_v1_execution_20260809.json"


class GoalOrientedS0ATests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_s0a_config(CONFIG)

    def test_reference_config_is_valid(self) -> None:
        self.assertEqual(len(validate_s0a_config(self.config)), 5)

    def test_patient_grouping_cannot_be_relabelled_as_lesion_split(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["expected_units"]["split_unit"] = "lesion"
        with self.assertRaisesRegex(S0AProtocolError, "patient-grouping"):
            validate_s0a_config(candidate)

    def test_solver_check_cannot_be_removed(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["required_checks"].remove(
            "solver_container_has_mesh_steady_forward_and_discrete_adjoint_or_verified_shape_gradient_capability"
        )
        with self.assertRaisesRegex(S0AProtocolError, "eleven checks"):
            validate_s0a_config(candidate)

    def test_s0a_cannot_authorize_gpu_or_outer_test(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["authorization"]["gpu_training"] = True
        with self.assertRaisesRegex(S0AProtocolError, "cannot authorize"):
            validate_s0a_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["authorization"]["outer_test"] = True
        with self.assertRaisesRegex(S0AProtocolError, "cannot authorize"):
            validate_s0a_config(candidate)

    def test_same_version_repair_rerun_cannot_be_opened(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate_rule"]["same_version_dependency_or_mapping_repair_rerun"] = True
        with self.assertRaisesRegex(S0AProtocolError, "no-repair"):
            validate_s0a_config(candidate)

    def test_staging_job_is_cpu_only_and_does_not_run_the_gate(self) -> None:
        script = STAGING_PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q ssu_a6gpu", script)
        self.assertIn("select=1:ncpus=4:mem=16gb", script)
        self.assertNotIn("ngpus=", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("singularity exec --nv", script)
        self.assertIn('"gate_evaluated":false', script)
        self.assertIn('"gpu_access":false', script)
        self.assertIn("AURORA_GIT_COMMIT", script)
        self.assertIn("status --porcelain", script)

    def test_staging_job_pins_all_official_archives(self) -> None:
        script = STAGING_PBS.read_text(encoding="utf-8")
        for token in (
            "49199083",
            "4821489080",
            "8d18b970978a303ed89618066919a1b1",
            "49199500",
            "34376",
            "12b92693c79587fb6dbab4638bfad8bc",
            "49201807",
            "10735821611",
            "e783d656ba51c6813aae9fca68565c17",
        ):
            self.assertIn(token, script)
        self.assertIn("--continue-at -", script)
        self.assertIn("7z x", script)

    def test_solver_preflight_reference_config_is_valid(self) -> None:
        config = load_solver_preflight_config(SOLVER_CONFIG)
        self.assertEqual(len(validate_solver_preflight_config(config)), 8)

    def test_solver_preflight_preserves_precompiled_ad_failure(self) -> None:
        config = load_solver_preflight_config(SOLVER_CONFIG)
        config["discovery_before_registration"]["official_precompiled_omp_release"][
            "eligible_for_s0a"
        ] = True
        with self.assertRaisesRegex(SolverPreflightProtocolError, "failure must be preserved"):
            validate_solver_preflight_config(config)

    def test_solver_preflight_requires_normal_and_reverse_ad(self) -> None:
        config = load_solver_preflight_config(SOLVER_CONFIG)
        config["build"]["flags"].remove("-Denable-autodiff=true")
        with self.assertRaisesRegex(SolverPreflightProtocolError, "normal and reverse-AD"):
            validate_solver_preflight_config(config)

    def test_solver_preflight_is_cpu_only_and_not_s0a(self) -> None:
        script = SOLVER_PBS.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=8:mem=32gb", script)
        self.assertNotIn("ngpus=", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("singularity exec --nv", script)
        self.assertNotIn("AURORA_STAGE_ROOT", script)
        self.assertIn('"scientific_gate_evaluated":false', script)
        self.assertIn('"medical_asset_access":false', script)
        self.assertIn('"gpu_access":false', script)
        self.assertIn("status --porcelain", script)

    def test_solver_preflight_pins_source_image_and_real_probe(self) -> None:
        script = SOLVER_PBS.read_text(encoding="utf-8")
        for token in (
            "12eb826f049ef7f67df974dfcb44cf36ee07c0f8",
            "790c80ec5b543487b5f8ecf8bb0f0e4d2cc67f3f",
            "8dc6f035de165a1e7c2e62c33e274ede60947d8a204b9dd2ae806fa12ccb9a72",
            "b3aa400aca6d2ba1f0bd03bd98d03d1fe7489a3bbb26969d72016360af8a5c9d",
            "cfb941d95508e6ddd79de1296584b1b3487be3a7d8b8369528c056faffc6731f",
            "e2139a98006bc296fb3e0992f4a05b35c85cc66fed346d813df4ec9032bad1f3",
        ):
            self.assertIn(token, script)
        self.assertIn("-Denable-autodiff=true", script)
        self.assertIn("-Denable-normal=true", script)
        self.assertIn("/opt/su2/bin/SU2_CFD -t 1 direct.cfg", script)
        self.assertIn("/opt/su2/bin/SU2_CFD_AD -t 1 adjoint.cfg", script)
        self.assertIn("surface sensitivity is identically zero", script)
        self.assertIn("same-source preflight rerun is forbidden", script)
        self.assertIn("A preflight record already exists for this public source", script)

    def test_stage_v1_execution_record_is_not_a_gate_result(self) -> None:
        record = json.loads(STAGING_V1_RECORD.read_text(encoding="utf-8"))
        self.assertEqual(record["scheduler"]["exit_status"], 28)
        self.assertEqual(record["access_boundary"]["verified_archive_bytes"], 0)
        self.assertEqual(record["verdict"]["s0a_gate"], "not_evaluated")
        self.assertFalse(record["diagnosis"]["exit_28_interpreted_as_proof_of_figshare_unavailability"])

    def test_stage_v2_reference_config_is_valid(self) -> None:
        config = load_staging_config(STAGING_V2_CONFIG)
        self.assertEqual(len(validate_staging_config(config)), 5)

    def test_stage_v2_cannot_relabel_v1_or_s0a(self) -> None:
        config = load_staging_config(STAGING_V2_CONFIG)
        config["decision"]["s0a_relabelled"] = True
        with self.assertRaisesRegex(StagingProtocolError, "cannot relabel"):
            validate_staging_config(config)

    def test_stage_v2_is_one_attempt_chunked_cpu_transport_only(self) -> None:
        script = STAGING_V2_PBS.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=4:mem=16gb", script)
        self.assertNotIn("ngpus=", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("singularity exec --nv", script)
        self.assertIn("readonly CHUNK_BYTES=67108864", script)
        self.assertIn('--range "$start-$end"', script)
        self.assertIn('if [ "$http_code" != "206" ]', script)
        self.assertIn('"scientific_gate_evaluated":false', script)
        self.assertIn('"identifier_mapping_attempted":false', script)
        self.assertIn("resubmission is forbidden", script)
        self.assertIn("md5sum", script)


if __name__ == "__main__":
    unittest.main()
