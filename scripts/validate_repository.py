"""Validate source notebooks and publication hygiene without reading raw datasets."""
import ast
import json
import re
import subprocess
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]

def main():
    for path in (ROOT / 'notebooks').glob('*.ipynb'):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                ast.parse(cell.source, feature_version=(3, 11))
                if cell.outputs or cell.execution_count is not None:
                    raise ValueError(f'Clear notebook outputs: {path.name}')
    for path in (ROOT / 'scripts').glob('*.py'):
        ast.parse(path.read_text(), feature_version=(3, 11))
    manifest = json.loads((ROOT / 'sources.json').read_text())
    if {s['city'] for s in manifest['sources']} != {'london', 'bristol'} or len(manifest['sources']) != 2:
        raise ValueError('Unexpected EDA source scope.')
    files = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True
    ).splitlines()
    for filename in files:
        path = Path(filename)
        if path.suffix in {'.csv', '.gz', '.parquet', '.delta'} or filename.startswith(('data/', '.env', '.venv/')):
            raise ValueError(f'Excluded artifact is publishable: {filename}')
        absolute = ROOT / path
        if absolute.stat().st_size > 2_000_000:
            raise ValueError(f'Review oversized artifact: {filename}')
        if absolute.suffix in {'.md', '.py', '.json', '.ipynb', '.txt'}:
            text = absolute.read_text()
            if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|dapi[a-f0-9]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)', text):
                raise ValueError(f'Possible credential in {filename}')
    print(f'Validated output-free notebooks, Python 3.11 syntax, A/B scope and {len(files)} publication artifacts.')

if __name__ == '__main__':
    main()
