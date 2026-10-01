# Copyright 2026 thinkingsage
# SPDX-License-Identifier: Apache-2.0

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "dataverse" / "scripts" / "deposit_inventory.py"
SPEC = importlib.util.spec_from_file_location("deposit_inventory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def draft_for(manifest):
    return {"status": "OK", "data": {"versionState": "DRAFT", "datasetPersistentId": "doi:10.99999/TEST", "files": [
        {"directoryLabel": str(Path(entry["dataverse_path"]).parent).replace(".", "", 1) if "/" not in entry["dataverse_path"] else entry["dataverse_path"].rsplit("/", 1)[0],
         "label": entry["dataverse_path"].rsplit("/", 1)[-1],
         "dataFile": {"id": index + 1, "filesize": entry["size_bytes"], "checksum": {"type": entry["checksum"]["algorithm"].upper(), "value": entry["checksum"]["value"]}}}
        for index, entry in enumerate(manifest["files"])
    ]}}


class DepositInventoryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.base = Path(self.scratch.name)
        self.root = self.base / "deposit"
        self.root.mkdir()
        (self.root / "nested space").mkdir()
        (self.root / "nested space" / "data file.txt").write_bytes(b"sample data\n")
        (self.root / ".notes").write_bytes(b"hidden\n")
        (self.root / "empty.bin").write_bytes(b"")
        self.manifest, _ = MODULE.manifest(str(self.root), "sha256", "data/raw")
        self.draft = draft_for(self.manifest)

    def tearDown(self):
        self.scratch.cleanup()

    def test_manifest_complete_names_bytes_digest_and_review(self):
        entries = {entry["relative_path"]: entry for entry in self.manifest["files"]}
        self.assertEqual(list(entries), [".notes", "empty.bin", "nested space/data file.txt"])
        self.assertEqual(entries["nested space/data file.txt"]["size_bytes"], 12)
        self.assertEqual(entries["nested space/data file.txt"]["checksum"]["value"], hashlib.sha256(b"sample data\n").hexdigest())
        self.assertEqual(entries[".notes"]["dataverse_path"], "data/raw/.notes")
        self.assertEqual(self.manifest["review"]["hidden_files"], [".notes"])
        self.assertEqual(self.manifest["review"]["empty_files"], ["empty.bin"])
        self.assertEqual(self.manifest["total_bytes"], 19)
        repeat, code = MODULE.manifest(str(self.root), "sha256", "data/raw")
        self.assertEqual(code, 0)
        self.assertEqual(repeat, self.manifest)

    def test_all_checksum_choices(self):
        for algorithm in MODULE.ALGORITHMS:
            result, code = MODULE.manifest(str(self.root), algorithm, "")
            self.assertEqual(code, 0)
            for entry in result["files"]:
                self.assertEqual(entry["checksum"]["value"], hashlib.new(algorithm, (self.root / entry["relative_path"]).read_bytes()).hexdigest())

    def test_duplicate_content_reported_without_removal(self):
        (self.root / "copy.txt").write_bytes(b"sample data\n")
        result, code = MODULE.manifest(str(self.root), "sha256", "")
        self.assertEqual(code, 0)
        self.assertEqual(result["file_count"], 4)
        self.assertEqual(result["review"]["duplicate_content"], [["copy.txt", "nested space/data file.txt"]])

    def test_file_symlink_refused(self):
        (self.root / "link.txt").symlink_to(self.root / ".notes")
        with self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.manifest(str(self.root), "sha256", "")

    def test_outside_directory_symlink_refused(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"outside")
        (self.root / "outside-link").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.manifest(str(self.root), "sha256", "")

    def test_root_symlink_and_unsafe_prefix_refused(self):
        link = self.base / "linked-root"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.manifest(str(link), "sha256", "")
        for prefix in ("../outside", "/absolute", "data//raw", "data/./raw"):
            with self.assertRaises(ValueError):
                MODULE.manifest(str(self.root), "sha256", prefix)

    def test_file_mutating_during_stream_is_refused(self):
        path = self.root / ".notes"
        real_digest = hashlib.sha256()
        class MutatingDigest:
            changed = False
            def update(self, data):
                real_digest.update(data)
                if not self.changed:
                    with path.open("ab") as target:
                        target.write(b"changed")
                    self.changed = True
            def hexdigest(self):
                return real_digest.hexdigest()
        with mock.patch.object(MODULE.hashlib, "new", return_value=MutatingDigest()):
            with self.assertRaisesRegex(ValueError, "changed"):
                MODULE.hash_file(path, "sha256")

    def test_complete_match_requires_explicit_draft(self):
        result, code = MODULE.reconcile(self.manifest, self.draft)
        self.assertEqual(code, 0)
        self.assertTrue(result["complete_match"])
        self.assertEqual(len(result["matched"]), 3)
        self.assertIn("not independent validation", result["evidence_limit"])
        released = copy.deepcopy(self.draft)
        released["data"]["versionState"] = "RELEASED"
        with self.assertRaisesRegex(ValueError, "DRAFT"):
            MODULE.reconcile(self.manifest, released)
        dataset = {"status": "OK", "data": {"latestVersion": self.draft["data"]}}
        self.assertEqual(MODULE.reconcile(self.manifest, dataset)[1], 0)

    def test_missing_and_unexpected_files(self):
        remote = copy.deepcopy(self.draft)
        removed = remote["data"]["files"].pop(0)
        changed = copy.deepcopy(removed)
        changed["label"] = "unexpected.txt"
        remote["data"]["files"].append(changed)
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(result["missing"], ["data/raw/.notes"])
        self.assertEqual(result["unexpected"], ["data/raw/unexpected.txt"])

    def test_changed_size_and_checksum(self):
        remote = copy.deepcopy(self.draft)
        record = remote["data"]["files"][0]["dataFile"]
        record["filesize"] += 1
        record["checksum"]["value"] = "0" * 64
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(len(result["size_mismatches"]), 1)
        self.assertEqual(len(result["checksum_mismatches"]), 1)
        self.assertEqual(len(result["matched"]), 2)

    def test_different_algorithm_is_incomparable(self):
        remote = copy.deepcopy(self.draft)
        remote["data"]["files"][0]["dataFile"]["checksum"] = {"type": "MD5", "value": "0" * 32}
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(len(result["incomparable_checksums"]), 1)
        self.assertEqual(result["checksum_mismatches"], [])

    def test_hyphenated_algorithm_and_hex_case_compare(self):
        remote = copy.deepcopy(self.draft)
        for entry in remote["data"]["files"]:
            entry["dataFile"]["checksum"]["type"] = "SHA-256"
            entry["dataFile"]["checksum"]["value"] = entry["dataFile"]["checksum"]["value"].upper()
        self.assertEqual(MODULE.reconcile(self.manifest, remote)[1], 0)

    def test_missing_or_malformed_size_checksum_incomplete(self):
        remote = copy.deepcopy(self.draft)
        del remote["data"]["files"][0]["dataFile"]["filesize"]
        remote["data"]["files"][0]["dataFile"]["checksum"]["value"] = "not-hex"
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(len(result["incomparable_sizes"]), 1)
        self.assertEqual(len(result["incomparable_checksums"]), 1)

    def test_remote_duplicates_do_not_silently_overwrite(self):
        remote = copy.deepcopy(self.draft)
        remote["data"]["files"].append(copy.deepcopy(remote["data"]["files"][0]))
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(result["remote_path_collisions"], ["data/raw/.notes"])
        self.assertEqual(len(result["matched"]), 2)

    def test_remote_case_collision_incomplete(self):
        remote = copy.deepcopy(self.draft)
        other = copy.deepcopy(remote["data"]["files"][0])
        other["label"] = ".NOTES"
        remote["data"]["files"].append(other)
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(result["remote_case_collisions"], [["data/raw/.NOTES", "data/raw/.notes"]])

    def test_ingested_original_never_reports_false_clean(self):
        remote = copy.deepcopy(self.draft)
        data = remote["data"]["files"][0]["dataFile"]
        data["originalFileName"] = ".notes"
        data["originalFileSize"] = 7
        data["originalFileFormat"] = "text/csv"
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(len(result["ingested_original_uncertainty"]), 1)
        self.assertEqual(len(result["matched"]), 2)

    def test_invalid_remote_paths_and_manifest_digest_refused(self):
        remote = copy.deepcopy(self.draft)
        remote["data"]["files"][0]["directoryLabel"] = "../outside"
        result, code = MODULE.reconcile(self.manifest, remote)
        self.assertEqual(code, 1)
        self.assertEqual(len(result["invalid_remote_paths"]), 1)
        damaged = copy.deepcopy(self.manifest)
        damaged["files"][0]["checksum"]["value"] = "bad"
        with self.assertRaisesRegex(ValueError, "checksum value"):
            MODULE.reconcile(damaged, self.draft)

    def test_cli_json_and_exit_codes(self):
        manifest_path = self.base / "manifest.json"
        draft_path = self.base / "draft.json"
        manifest_path.write_text(json.dumps(self.manifest))
        draft_path.write_text(json.dumps(self.draft))
        base = [sys.executable, str(SCRIPT)]
        outcome = subprocess.run(base + ["reconcile", "--manifest", str(manifest_path), "--draft-json", str(draft_path)], capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertTrue(json.loads(outcome.stdout)["complete_match"])
        self.draft["data"]["files"] = []
        draft_path.write_text(json.dumps(self.draft))
        outcome = subprocess.run(base + ["reconcile", "--manifest", str(manifest_path), "--draft-json", str(draft_path)], capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 1)
        self.assertFalse(json.loads(outcome.stdout)["complete_match"])
        draft_path.write_text("not json")
        outcome = subprocess.run(base + ["reconcile", "--manifest", str(manifest_path), "--draft-json", str(draft_path)], capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 2)
        self.assertEqual(json.loads(outcome.stdout)["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
