"""Execute the EDA notebook locally without persisting cell outputs."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
notebook = nbformat.read(root / 'notebooks/01_eda_london_bristol.ipynb', as_version=4)
NotebookClient(notebook, timeout=600, kernel_name='python3', resources={'metadata': {'path': str(root)}}).execute()
errors = [o for c in notebook.cells if c.cell_type == 'code' for o in c.outputs if o.output_type == 'error']
if errors:
    raise RuntimeError(errors)
print('EDA execution completed. Aggregate findings: docs/eda_findings.md')
