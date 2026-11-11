"""Validate notebooks, source manifest, and publication hygiene."""

import ast
import json
import re
import subprocess
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_CITIES = {"london", "bristol", "greater-manchester"}
BASE_URL = "https://data.insideairbnb.com/united-kingdom/england"


def validate_manifest():
    records = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["sources"]
    cities = [item["city"] for item in records]
    if len(cities) != len(set(cities)) or not {"london", "bristol"}.issubset(cities):
        raise ValueError("Manifest must contain unique cities and both original A/B sources.")
    if not set(cities) <= ALLOWED_CITIES:
        raise ValueError(f"Unexpected cities: {set(cities) - ALLOWED_CITIES}")

    for item in records:
        city, date = item["city"], item["snapshot_date"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError(f"Invalid snapshot date: {city}")
        if item["url"] != f"{BASE_URL}/{city}/{date}/data/listings.csv.gz":
            raise ValueError(f"Invalid URL: {city}")
        if item["relative_path"] != f"data/raw/{city}/{date}/listings.csv.gz":
            raise ValueError(f"Invalid relative path: {city}")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", item.get("sha256", "")):
            raise ValueError(f"Missing or invalid SHA-256: {city}")
        if type(item.get("bytes")) is not int or item["bytes"] <= 0:
            raise ValueError(f"Invalid source file size: {city}")
    return cities


def main():
    cities = validate_manifest()
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue

            # Check that notebook outputs are cleared.
            if cell.outputs or cell.execution_count is not None:
                raise ValueError(f"Clear notebook outputs: {path.name}")

            source = cell.source.lstrip()

            # Skip non-Python Databricks cells.
            if source.startswith(("%sql", "%md", "%scala", "%r", "%sh", "%fs", "%pip")):
                continue

            # Check Python syntax.
            ast.parse(cell.source, feature_version=(3, 11))
    for path in (ROOT / "scripts").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 11))

    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, text=True
    ).splitlines()
    for filename in files:
        path = Path(filename)
        if path.suffix in {".csv", ".gz", ".parquet", ".delta"} or filename.startswith(("data/", ".env", ".venv/")):
            raise ValueError(f"Excluded artifact is publishable: {filename}")
        absolute = ROOT / path
        if not absolute.is_file():
            continue  # Deleted tracked file in the working tree.
        if absolute.stat().st_size > 2_000_000:
            raise ValueError(f"Review oversized artifact: {filename}")
        if absolute.suffix in {".md", ".py", ".json", ".ipynb", ".txt"}:
            text = absolute.read_text(encoding="utf-8")
            if re.search(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|dapi[a-f0-9]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)", text):
                raise ValueError(f"Possible credential in {filename}")
    print(f"Validated notebooks, source manifest ({', '.join(cities)}), and {len(files)} publication artifacts.")


if __name__ == "__main__":
    main()
