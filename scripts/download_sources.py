"""Retrieve pinned A/B snapshots, verify checksums, and preserve existing inputs."""
import hashlib
import json
import os
import re
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / 'sources.json').read_text())
    records = manifest['sources']
    if len(records) != 2 or {s['city'] for s in records} != {'london', 'bristol'}:
        raise ValueError('Only London and Bristol are permitted.')
    page = urllib.request.urlopen('https://insideairbnb.com/get-the-data/', timeout=60).read().decode()
    for source in records:
        city = source['city']
        allowed = f"https://data.insideairbnb.com/united-kingdom/england/{city}/{source['snapshot_date']}/data/listings.csv.gz"
        relative = f"data/raw/{city}/{source['snapshot_date']}/listings.csv.gz"
        if source['url'] != allowed or source['relative_path'] != relative:
            raise ValueError('Unexpected URL or path in source manifest.')
        dates = re.findall(rf'https://data\.insideairbnb\.com/united-kingdom/england/{city}/(\d{{4}}-\d{{2}}-\d{{2}})/data/listings\.csv\.gz', page)
        if not dates:
            raise RuntimeError(f'Cannot verify the latest snapshot for {city}.')
        if max(dates) != source['snapshot_date']:
            raise RuntimeError(f'Newer {city} snapshot exists: {max(dates)}. Review and version a new manifest before a new study; preserve frozen sources.')
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            with target.open('rb') as handle:
                digest = hashlib.file_digest(handle, 'sha256').hexdigest()
            if digest != source['sha256']:
                raise ValueError(f'Existing input has the wrong checksum: {city}; it was not overwritten.')
        else:
            with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
                staged = Path(temporary) / 'download.gz'
                with urllib.request.urlopen(allowed, timeout=120) as response, staged.open('wb') as out:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)
                with staged.open('rb') as handle:
                    digest = hashlib.file_digest(handle, 'sha256').hexdigest()
                if digest != source['sha256']:
                    raise ValueError(f'Download checksum mismatch: {city}.')
                # Same-filesystem linking publishes a complete file without replacement.
                os.link(staged, target)
        print(f"{city}: {source['snapshot_date']}, checksum verified")

if __name__ == '__main__':
    main()
