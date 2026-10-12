#!/usr/bin/env python3
"""Validate *live* Foundry V13 required-module manifests and archive contents.

This intentionally performs actual HTTPS GET requests, not just JSON syntax checks
or URL string checks. Saves a machine-readable report even when dependencies fail.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Foundry-V13-Live-Dependency-Audit/1.0"
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_BYTES = 850 * 1024 * 1024


def get_bytes(url, label, max_bytes, outfile=None):
    if not isinstance(url, str) or not url.startswith("https://") or "/blob/" in url:
        raise ValueError(f"{label}: requires a direct HTTPS URL, not a GitHub HTML/blob page: {url!r}")
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json, application/zip, application/octet-stream, */*",
    })
    with urllib.request.urlopen(request, timeout=75) as response:
        final_url = response.geturl()
        if not final_url.startswith("https://"):
            raise ValueError(f"{label}: insecure redirect: {final_url!r}")
        status = response.status
        if status != 200:
            raise ValueError(f"{label}: HTTP {status} at {final_url}")
        ctype = response.headers.get("Content-Type", "")
        raw = bytearray()
        hashobj = hashlib.sha256()
        total = 0
        if outfile is None:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"{label}: response exceeds {max_bytes} bytes")
                raw.extend(chunk)
                hashobj.update(chunk)
        else:
            with open(outfile, "wb") as dest:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError(f"{label}: response exceeds {max_bytes} bytes")
                    hashobj.update(chunk)
                    dest.write(chunk)
    return {
        "status": status,
        "final_url": final_url,
        "content_type": ctype,
        "bytes": total,
        "sha256": hashobj.hexdigest(),
    }, bytes(raw)


def parse_manifest(url):
    evidence, raw = get_bytes(url, "manifest", MAX_MANIFEST_BYTES)
    if raw.lstrip().startswith((b"<", b"<!DOCTYPE", b"<!doctype")):
        raise ValueError(f"HTML response, not manifest JSON; content-type={evidence['content_type']}, final={evidence['final_url']}")
    try:
        manifest = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as ex:
        raise ValueError(f"Invalid JSON (content-type={evidence['content_type']}, final={evidence['final_url']}): {ex}") from ex
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a JSON object")
    return manifest, evidence


def compatible_v13(compat):
    def number(v, default):
        try:
            return int(str(v).split(".")[0])
        except (ValueError, TypeError):
            return default
    return number(compat.get("minimum"), -1) <= 13 <= number(compat.get("maximum"), 999)


def validate_package(manifest, package):
    ident = package["id"]
    version = str(package["expectedVersion"])
    if manifest.get("id") != ident:
        raise ValueError(f"module ID mismatch: expected {ident!r}; got {manifest.get('id')!r}")
    if str(manifest.get("version")) != version:
        raise ValueError(f"version mismatch: expected {version!r}; got {manifest.get('version')!r}")
    if not compatible_v13(manifest.get("compatibility") or {}):
        raise ValueError(f"no V13 compatibility: {manifest.get('compatibility')!r}")
    download = manifest.get("download")
    if not isinstance(download, str) or not download.startswith("https://") or "/blob/" in download:
        raise ValueError(f"invalid ZIP download URL {download!r}")
    if "/releases/latest/" in download:
        raise ValueError(f"download URL not pinned to a release: {download!r}")
    return download


def validate_archive(download_url, package, td):
    filepath = str(Path(td) / (package["id"] + ".zip"))
    evidence, _ = get_bytes(download_url, "archive", MAX_ARCHIVE_BYTES, outfile=filepath)
    with open(filepath, "rb") as f:
        if f.read(4) != b"PK\x03\x04":
            raise ValueError(f"archive is not a ZIP file; received {evidence['content_type']} from {evidence['final_url']}")
    with zipfile.ZipFile(filepath) as z:
        candidates = [n for n in z.namelist() if n.endswith("module.json") and n.count("/") <= 2]
        hits = []
        for n in candidates:
            if z.getinfo(n).file_size > MAX_MANIFEST_BYTES:
                continue
            try:
                m = json.loads(z.read(n).decode("utf-8-sig"))
            except (ValueError, UnicodeDecodeError):
                continue
            if m.get("id") == package["id"]:
                hits.append((n, m))
        if len(hits) != 1:
            raise ValueError(f"expected exactly one embedded module.json ID {package['id']}; found {len(hits)}")
        path, embedded = hits[0]
        if str(embedded.get("version")) != str(package["expectedVersion"]):
            raise ValueError(f"archive embedded version differs: {embedded.get('version')!r}")
        if not compatible_v13(embedded.get("compatibility") or {}):
            raise ValueError(f"archive embedded module is not V13-compatible: {embedded.get('compatibility')!r}")
    evidence["embedded_manifest"] = path
    return evidence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="validation/v13-live-report.json")
    ap.add_argument("--archives", action="store_true", help="download and validate all actual ZIP packages")
    args = ap.parse_args()
    reg = json.loads((ROOT / "dependencies-v13.json").read_text())
    meta = json.loads((ROOT / "module.json").read_text())
    required = meta.get("relationships", {}).get("requires", [])
    packages = {p["id"]: p for p in reg["packages"] if p.get("installMode") == "manifest"}
    report = {
        "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "meta_version": meta.get("version"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "archives_checked": args.archives,
        "modules": [],
        "failed": [],
    }
    try:
        ids = [x["id"] for x in required]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate IDs in requires")
        if set(ids) != set(packages):
            raise ValueError(f"required IDs differ from auto-install registry: {sorted(set(ids)^set(packages))}")
        for dep in required:
            p = packages[dep["id"]]
            if dep.get("manifest") != p["manifest"]:
                raise ValueError(f"require URL differs from registry for {dep['id']}")
        with tempfile.TemporaryDirectory() as td:
            for p in packages.values():
                item = {"id": p["id"], "expected_version": p["expectedVersion"], "manifest_url": p["manifest"]}
                try:
                    manifest, evidence = parse_manifest(p["manifest"])
                    item["manifest_http"] = evidence
                    archive_url = validate_package(manifest, p)
                    item["download_url"] = archive_url
                    item["manifest_ok"] = True
                    if args.archives:
                        item["archive_http"] = validate_archive(archive_url, p, td)
                        item["archive_ok"] = True
                    print(f"PASS {p['id']} manifest{'+archive' if args.archives else ''}: {p['expectedVersion']}", flush=True)
                except Exception as exc:
                    item["manifest_ok"] = item.get("manifest_ok", False)
                    item["archive_ok"] = False if args.archives else None
                    item["error"] = f"{type(exc).__name__}: {exc}"
                    report["failed"].append(p["id"])
                    print(f"FAIL {p['id']}: {item['error']}", flush=True)
                report["modules"].append(item)
    except Exception as exc:
        report["failed"].append("registry")
        report["registry_error"] = f"{type(exc).__name__}: {exc}"
    report["total"] = len(report["modules"])
    report["passed"] = report["total"] - len([m for m in report["modules"] if m["id"] in report["failed"]])
    report["success"] = not report["failed"] and report["total"] == len(packages)
    dest = ROOT / args.report
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"AUDIT REPORT: {dest}; passed={report['passed']}/{report['total']}; failures={report['failed']}", flush=True)
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
