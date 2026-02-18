"""
Data cleaning utilities for AutoScience.
Provides CSV loading, basic cleaning, and optional schema inference.
"""

from pathlib import Path
from typing import Optional

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore


def clean_csv(
    csv_path: Path,
    output_path: Optional[Path] = None,
    drop_duplicates: bool = True,
    drop_na_all: bool = False,
    **read_csv_kwargs: object,
) -> "pd.DataFrame":
    """
    Load a CSV, apply basic cleaning, and optionally save.
    :param csv_path: Path to input CSV.
    :param output_path: If set, write cleaned DataFrame here.
    :param drop_duplicates: Remove duplicate rows.
    :param drop_na_all: Remove rows that are all NaN.
    :param read_csv_kwargs: Passed to pandas.read_csv.
    :return: Cleaned DataFrame.
    """
    if pd is None:
        raise ImportError("pandas is required for data cleaning. Install with: pip install pandas")
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path, **read_csv_kwargs)
    if drop_na_all:
        df = df.dropna(how="all")
    if drop_duplicates:
        df = df.drop_duplicates()
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
    return df
