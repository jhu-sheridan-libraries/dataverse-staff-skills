#!/usr/bin/env python3
# Copyright 2026 thinkingsage
# SPDX-License-Identifier: Apache-2.0
"""Inventory local deposit files or reconcile them with saved Dataverse draft JSON."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata


ALGORITHMS = ("sha256", "sha1", "sha512", "md5")
EVIDENCE_LIMIT = (
    "Compares a saved local manifest with saved Dataverse DRAFT metadata. "
    "A checksum supplied by an uploader is not independent validation of remote bytes. "
    "This report does not establish current server state or publication readiness."
)


def safe_path(value, allow_empty=False):
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        raise ValueError("Paths must be relative strings using / separators.")
    if not value and allow_empty:
        return ""
    if not value or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Paths cannot be empty, absolute, or contain empty, dot or dot-dot segments.")
    return value


def collisions(paths):
    exact, folded = {}, {}
    for path in paths:
        exact.setdefault(path, 0)
        exact[path] += 1
        folded.setdefault(unicodedata.normalize("NFC", path).casefold(), set()).add(path)
    return (
        sorted(path for path, count in exact.items() if count > 1),
        sorted(sorted(group) for group in folded.values() if len(group) > 1),
    )


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def local_paths(root):
    paths = []

    def raise_walk_error(error):
        raise error

    for folder, directories, names in os.walk(root, followlinks=False, onerror=raise_walk_error):
        for name in directories + names:
            path = Path(folder) / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise ValueError("Refusing symlink: " + str(path.relative_to(root)))
            if not path.resolve().is_relative_to(root):
                raise ValueError("Refusing path outside selected root: " + str(path))
            if name in names:
                if not stat.S_ISREG(info.st_mode):
                    raise ValueError("Refusing non-regular file: " + str(path.relative_to(root)))
                paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def hash_file(path, algorithm):
    before = signature(path.lstat())
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    digest = hashlib.new(algorithm)
    count = 0
    with os.fdopen(descriptor, "rb") as source:
        opened = os.fstat(source.fileno())
        if not stat.S_ISREG(opened.st_mode) or signature(opened) != before:
            raise ValueError("File changed before reading: " + str(path))
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            count += len(chunk)
            digest.update(chunk)
        after = signature(os.fstat(source.fileno()))
    if before != after or signature(path.lstat()) != before or count != opened.st_size:
        raise ValueError("File changed while reading: " + str(path))
    return count, digest.hexdigest(), before


def manifest(root_argument, algorithm, prefix):
    selected = Path(root_argument).expanduser()
    if selected.is_symlink():
        raise ValueError("The selected root must not be a symlink.")
    root = selected.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a directory containing the complete intended deposit.")
    prefix = safe_path(prefix, allow_empty=True)
    paths = local_paths(root)
    files, signatures = [], {}
    for path in paths:
        relative = safe_path(path.relative_to(root).as_posix())
        size, checksum, before = hash_file(path, algorithm)
        signatures[path] = before
        files.append({
            "relative_path": relative,
            "dataverse_path": (prefix + "/" if prefix else "") + relative,
            "size_bytes": size,
            "checksum": {"algorithm": algorithm, "value": checksum},
        })
    if local_paths(root) != paths or any(signature(path.lstat()) != signatures[path] for path in paths):
        raise ValueError("The selected files changed during inventory; make a fresh manifest.")
    exact, case = collisions([entry["dataverse_path"] for entry in files])
    content = {}
    for entry in files:
        key = (entry["size_bytes"], entry["checksum"]["value"])
        content.setdefault(key, []).append(entry["dataverse_path"])
    report = {
        "schema_version": 1,
        "kind": "dataverse_local_manifest",
        "status": "path_collisions" if exact or case else "inventory_created",
        "root": str(root),
        "prefix": prefix,
        "checksum_algorithm": algorithm,
        "file_count": len(files),
        "total_bytes": sum(entry["size_bytes"] for entry in files),
        "files": files,
        "review": {
            "hidden_files": [entry["relative_path"] for entry in files if any(part.startswith(".") for part in entry["relative_path"].split("/"))],
            "empty_files": [entry["relative_path"] for entry in files if entry["size_bytes"] == 0],
            "duplicate_content": sorted(sorted(group) for group in content.values() if len(group) > 1),
            "path_collisions": exact,
            "case_collisions": case,
        },
    }
    return report, 1 if exact or case else 0


def load_json(path):
    with open(path, encoding="utf-8") as source:
        return json.load(source)


def validate_manifest(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or payload.get("kind") != "dataverse_local_manifest":
        raise ValueError("Expected a schema_version 1 manifest created by this helper.")
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValueError("Manifest files must be a list.")
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("Invalid manifest file record.")
        safe_path(entry.get("relative_path"))
        safe_path(entry.get("dataverse_path"))
        if type(entry.get("size_bytes")) is not int or entry["size_bytes"] < 0:
            raise ValueError("Manifest sizes must be nonnegative integers.")
        checksum = entry.get("checksum")
        if not isinstance(checksum, dict) or checksum.get("algorithm") not in ALGORITHMS:
            raise ValueError("Invalid manifest checksum algorithm.")
        length = hashlib.new(checksum["algorithm"]).digest_size * 2
        if not isinstance(checksum.get("value"), str) or not re.fullmatch(r"[0-9a-fA-F]{" + str(length) + r"}", checksum["value"]):
            raise ValueError("Invalid manifest checksum value.")
    return files


def draft_version(payload):
    if not isinstance(payload, dict):
        raise ValueError("Draft JSON must contain a Native API object.")
    if "data" in payload:
        if payload.get("status") != "OK":
            raise ValueError("Saved Native API response does not have status OK.")
        payload = payload["data"]
    if not isinstance(payload, dict):
        raise ValueError("Native API data must be an object.")
    if "latestVersion" in payload:
        payload = payload["latestVersion"]
    if not isinstance(payload, dict) or payload.get("versionState") != "DRAFT":
        raise ValueError("Reconciliation requires versionState DRAFT; published/latest-published snapshots are not accepted.")
    if not isinstance(payload.get("files"), list):
        raise ValueError("Draft JSON must contain the complete files list.")
    return payload


def remote_records(version):
    records, invalid, ingested = [], [], []
    for index, entry in enumerate(version["files"]):
        if not isinstance(entry, dict) or not isinstance(entry.get("dataFile"), dict):
            raise ValueError("Draft file records must include dataFile objects.")
        data = entry["dataFile"]
        label, directory = entry.get("label"), entry.get("directoryLabel", "")
        try:
            if not isinstance(label, str) or "/" in label:
                raise ValueError("File label must be a single filename.")
            safe_path(label)
            safe_path(directory, allow_empty=True)
            path = (directory + "/" if directory else "") + label
        except ValueError as error:
            invalid.append({"file_index": index, "data_file_id": data.get("id"), "reason": str(error)})
            continue
        record = {"path": path, "data": data}
        records.append(record)
        if (
            any(data.get(key) not in (None, "") for key in ("originalFileName", "originalFileSize", "originalFileFormat", "UNF"))
            or data.get("isTabularData") is True
            or data.get("tabularData") is True
        ):
            ingested.append({
                "path": path,
                "original_filename": data.get("originalFileName"),
                "original_size_bytes": data.get("originalFileSize"),
                "reason": "Ingested/tabular metadata may describe archival bytes; this snapshot does not independently verify the uploaded original.",
            })
    return records, invalid, ingested


def reconcile(manifest_payload, draft_payload):
    local = validate_manifest(manifest_payload)
    version = draft_version(draft_payload)
    remote, invalid, ingested = remote_records(version)
    local_paths = [entry["dataverse_path"] for entry in local]
    remote_paths = [entry["path"] for entry in remote]
    local_exact, local_case = collisions(local_paths)
    remote_exact, remote_case = collisions(remote_paths)
    result = {
        "schema_version": 1,
        "kind": "dataverse_draft_reconciliation",
        "evidence_limit": EVIDENCE_LIMIT,
        "draft": {"dataset_persistent_id": version.get("datasetPersistentId"), "version_state": "DRAFT"},
        "matched": [],
        "missing": sorted(set(local_paths) - set(remote_paths)),
        "unexpected": sorted(set(remote_paths) - set(local_paths)),
        "size_mismatches": [],
        "incomparable_sizes": [],
        "checksum_mismatches": [],
        "incomparable_checksums": [],
        "ingested_original_uncertainty": ingested,
        "invalid_remote_paths": invalid,
        "local_path_collisions": local_exact,
        "local_case_collisions": local_case,
        "remote_path_collisions": remote_exact,
        "remote_case_collisions": remote_case,
    }
    local_by_path = {entry["dataverse_path"]: entry for entry in local if entry["dataverse_path"] not in local_exact}
    remote_by_path = {entry["path"]: entry["data"] for entry in remote if entry["path"] not in remote_exact}
    ingest_paths = {entry["path"] for entry in ingested}
    for path in sorted(set(local_by_path) & set(remote_by_path)):
        entry, data = local_by_path[path], remote_by_path[path]
        size = data.get("filesize")
        match = True
        if type(size) is not int or size < 0:
            result["incomparable_sizes"].append({"path": path, "draft_size_bytes": size})
            match = False
        elif size != entry["size_bytes"]:
            result["size_mismatches"].append({"path": path, "local_size_bytes": entry["size_bytes"], "draft_size_bytes": size})
            match = False
        checksum = data.get("checksum")
        checksum = checksum if isinstance(checksum, dict) else {}
        algorithm = checksum.get("type")
        normalized = algorithm.lower().replace("-", "") if isinstance(algorithm, str) else None
        value = checksum.get("value")
        if normalized != entry["checksum"]["algorithm"]:
            result["incomparable_checksums"].append({"path": path, "local_algorithm": entry["checksum"]["algorithm"], "draft_algorithm": algorithm, "reason": "Different or absent algorithms; make a manifest with the reported supported algorithm."})
            match = False
        elif not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{" + str(len(entry["checksum"]["value"])) + r"}", value):
            result["incomparable_checksums"].append({"path": path, "draft_algorithm": algorithm, "reason": "Draft checksum is absent or malformed."})
            match = False
        elif value.lower() != entry["checksum"]["value"].lower():
            result["checksum_mismatches"].append({"path": path, "algorithm": normalized, "local_checksum": entry["checksum"]["value"], "draft_checksum": value})
            match = False
        if match and path not in ingest_paths:
            result["matched"].append({"path": path, "data_file_id": data.get("id")})
    issue_fields = [key for key in result if key not in ("schema_version", "kind", "evidence_limit", "draft", "matched")]
    complete = not any(result[key] for key in issue_fields)
    result["complete_match"] = complete
    result["status"] = "inventory_metadata_match" if complete else "incomplete"
    return result, 0 if complete else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read-only local inventory and saved Dataverse DRAFT reconciliation. No network, credentials, or source modifications.",
        epilog=(
            "JSON reports go to stdout; save them OUTSIDE the selected deposit root. "
            "Exit 0: manifest created (review hidden/empty/duplicate flags), or complete saved-metadata match. "
            "Exit 1: path/case collisions in a manifest, or incomplete reconciliation. "
            "Exit 2: invalid input, unreadable/changing files, symlinks or other unsafe filesystem entries. "
            "Checksums use streamed bytes; a saved-metadata match is not independent remote byte validation."
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("manifest", help="Include every regular file under an explicitly selected directory.")
    inventory.add_argument("root")
    inventory.add_argument("--checksum", choices=ALGORITHMS, default="sha256")
    inventory.add_argument("--prefix", default="", help="Relative Dataverse directoryLabel prefix, e.g. data/raw.")
    compare = commands.add_parser("reconcile", help="Compare a saved manifest with a complete saved canonical DRAFT files list.")
    compare.add_argument("--manifest", required=True)
    compare.add_argument("--draft-json", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "manifest":
            report, code = manifest(args.root, args.checksum, args.prefix)
        else:
            report, code = reconcile(load_json(args.manifest), load_json(args.draft_json))
    except (OSError, ValueError) as error:
        report, code = {"schema_version": 1, "kind": "dataverse_inventory_error", "status": "error", "message": str(error)}, 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
