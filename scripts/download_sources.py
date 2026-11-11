"""Download pinned Inside Airbnb snapshots and verify file integrity."""

import hashlib
import json
import os
import re
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_CITIES = {"london", "bristol", "greater-manchester"}
BASE_URL = "https://data.insideairbnb.com/united-kingdom/england"


def validate_sources(records):
    cities = [record["city"] for record in records]
    if len(cities) != len(set(cities)) or not {"london", "bristol"}.issubset(cities):
        raise ValueError("Manifest must contain unique cities and the original A/B sources.")
    if not set(cities) <= ALLOWED_CITIES:
        raise ValueError(f"Unexpected city in manifest: {set(cities) - ALLOWED_CITIES}")

    for source in records:
        city, date = source["city"], source["snapshot_date"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError(f"Invalid snapshot date for {city}")
        relative = f"data/raw/{city}/{date}/listings.csv.gz"
        url = f"{BASE_URL}/{city}/{date}/data/listings.csv.gz"
        if source["relative_path"] != relative or source["url"] != url:
            raise ValueError(f"Unexpected URL or relative path for {city}")
        if not re.fullmatch(r"[a-fA-F0-9]{64}", source.get("sha256", "")):
            raise ValueError(f"Missing or invalid SHA-256 for {city}")
        if type(source.get("bytes")) is not int or source["bytes"] <= 0:
            raise ValueError(f"Invalid file size for {city}")


def verify(path, source):
    if path.stat().st_size != source["bytes"]:
        raise ValueError(f"Unexpected file size: {path}")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if digest.lower() != source["sha256"].lower():
        raise ValueError(f"SHA-256 mismatch: {path}")


def main():
    records = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["sources"]
    validate_sources(records)

    for source in records:
        target = ROOT / source["relative_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
                staged = Path(temporary) / "download.gz"
                with urllib.request.urlopen(source["url"], timeout=120) as response, staged.open("wb") as out:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)
                verify(staged, source)
                os.link(staged, target)  # Publish without replacing existing data.
        verify(target, source)
        print(f"{source['city']}: {source['snapshot_date']}, checksum verified")


if __name__ == "__main__":
    main()
