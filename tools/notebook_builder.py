"""
Build a Jupyter notebook (.ipynb) from successful script contents for reproducibility.
"""

from pathlib import Path
from typing import Sequence

try:
    import nbformat
    from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
except ImportError:
    nbformat = None  # type: ignore
    new_notebook = new_code_cell = new_markdown_cell = None  # type: ignore


def build_notebook_from_scripts(
    script_paths: Sequence[Path],
    output_path: Path,
    title: str = "Reproducible Analysis",
    markdown_intro: str = "",
) -> Path:
    """
    Create a single .ipynb that runs the given scripts in order.
    Each script's content becomes one or more code cells; use a single cell per script
    for simplicity so execution order matches the pipeline.
    :param script_paths: Ordered list of paths to .py files (successful analysis/viz scripts).
    :param output_path: Where to write the .ipynb.
    :param title: Notebook title (first markdown cell).
    :param markdown_intro: Optional intro markdown after the title.
    :return: output_path.
    """
    if nbformat is None:
        raise ImportError("nbformat is required. Install with: pip install nbformat")
    nb = new_notebook()
    cells = [new_markdown_cell(f"# {title}\n\n{markdown_intro}".strip())]
    for path in script_paths:
        p = Path(path)
        if not p.exists():
            continue
        code = p.read_text(encoding="utf-8")
        cells.append(new_code_cell(code))
    nb["cells"] = cells
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    return out
