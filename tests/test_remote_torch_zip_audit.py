import pickle
import re
import unittest
from unittest import mock

from aurora.remote_torch_zip_audit import (
    extract_case_like_strings,
    load_huggingface_release_case_ids,
)


class RemoteTorchZipAuditTests(unittest.TestCase):
    def test_extracts_unique_case_identifiers_without_unpickling(self):
        payload = {
            "registered_data_list": [
                {"case": "stable_2"},
                {"case": "stable_1"},
                {"case": "Eyad_shape_4"},
            ],
            "mesh_data": {"cases": ["stable_2", "stable_1", "Eyad_shape_4"]},
        }
        raw = pickle.dumps(payload, protocol=4)
        found = extract_case_like_strings(
            raw,
            (re.compile(r"stable_[0-9]+"), re.compile(r"Eyad_shape_[0-9]+")),
        )
        self.assertEqual(found, ["Eyad_shape_4", "stable_1", "stable_2"])

    def test_ignores_nonmatching_strings(self):
        raw = pickle.dumps({"case": "not_a_case", "other": "stable_bad"})
        self.assertEqual(
            extract_case_like_strings(raw, (re.compile(r"stable_[0-9]+"),)),
            [],
        )

    def test_release_inventory_uses_directory_names_only(self):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        with mock.patch(
            "aurora.remote_torch_zip_audit.urllib.request.urlopen",
            return_value=response,
        ), mock.patch(
            "aurora.remote_torch_zip_audit.json.load",
            return_value={
                "siblings": [
                    {"rfilename": "transient_data/stable_1/wall_data.pt"},
                    {"rfilename": "transient_data/stable_1/shape.obj"},
                    {"rfilename": "transient_data/stable_2/wall_data.pt"},
                    {"rfilename": "processed_data/stable_3"},
                ]
            },
        ):
            self.assertEqual(
                load_huggingface_release_case_ids("https://example.invalid/api"),
                ["stable_1", "stable_2"],
            )


if __name__ == "__main__":
    unittest.main()
