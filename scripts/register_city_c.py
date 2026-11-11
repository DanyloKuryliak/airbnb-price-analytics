"""Register the frozen Greater Manchester file in sources.json after downloading it."""

import argparse
import gzip
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITY = "greater-manchester"
SNAPSHOT = "2026-09-22"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True, help="Local, downloaded Manchester listings.csv.gz")
    args = parser.parse_args()
    source_file = args.file.expanduser().resolve()
    if not source_file.is_file():
        raise FileNotFoundError(source_file)
    with source_file.open("rb") as handle:
        if handle.read(2) != b"\x1f\x8b":
            raise ValueError("Not a gzip file")
    with gzip.open(source_file, "rb") as handle:
        if b"id" not in handle.readline().lower():
            raise ValueError("Unexpected listings CSV header")
    with source_file.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()

    path = ROOT / "sources.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    existing = {item["city"]: item for item in manifest["sources"]}
    record = {
        "city": CITY,
        "snapshot_date": SNAPSHOT,
        "url": f"https://data.insideairbnb.com/united-kingdom/england/{CITY}/{SNAPSHOT}/data/listings.csv.gz",
        "relative_path": f"data/raw/{CITY}/{SNAPSHOT}/listings.csv.gz",
        "sha256": sha256,
        "bytes": source_file.stat().st_size,
    }
    if CITY in existing and existing[CITY] != record:
        raise ValueError("Manchester is already registered with different metadata; check the frozen source.")
    if CITY not in existing:
        manifest["sources"].append(record)
    manifest["verified_on"] = date.today().isoformat()
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Registered {CITY} with SHA-256 {sha256}, {record['bytes']} bytes")
    print("Source CSV was NOT added to Git. Keep data/raw/ ignored.")


if __name__ == "__main__":
    main()
