#!/usr/bin/env python3
"""
CleanR - Professional CSV Cleaner
Fast, memory-efficient, and robust CSV processing with advanced column operations.
"""

import sys
import time
import argparse
import functools
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

VERSION = "1.0.0"
DEFAULT_CHUNK_SIZE = 100_000
SUPPORTED_ENCODINGS = ["utf-8", "latin1", "iso-8859-1", "cp1252", "utf-16", "utf-8-sig"]


def timer(func):
    """Decorator that logs execution time of slow operations."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = func(self, *args, **kwargs)
        elapsed = time.time() - start
        if elapsed > 0.1 and self.verbose:
            label = func.__name__.replace("_", " ").title()
            print(f"  {label}: {elapsed:.2f}s")
        return result
    return wrapper


class CleanR:
    """Main CSV cleaning engine."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.stats: Dict = {
            "start_time": time.time(),
            "rows_processed": 0,
            "rows_removed": 0,
            "memory_saved_mb": 0.0,
            "success": False,
        }

    def _log(self, message: str):
        if self.verbose:
            print(message)

    @timer
    def load_file(
        self,
        filepath: Path,
        encoding: Optional[str] = None,
        quick: bool = False,
        chunk_size: Optional[int] = None,
    ) -> pd.DataFrame:
        """Load CSV with encoding fallback and optional chunked reading."""
        if not filepath.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")

        encodings = [encoding] if encoding else SUPPORTED_ENCODINGS
        last_error: Optional[Exception] = None

        for enc in encodings:
            try:
                self._log(f"  Trying encoding: {enc}")
                read_kwargs = dict(
                    encoding=enc,
                    dtype=str if quick else None,
                    low_memory=False,
                    on_bad_lines="skip",
                )
                if chunk_size and chunk_size > 0:
                    chunks = list(pd.read_csv(filepath, chunksize=chunk_size, **read_kwargs))
                    df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
                else:
                    df = pd.read_csv(filepath, **read_kwargs)

                if df.empty:
                    raise ValueError("No data loaded from CSV.")

                self.stats["rows_processed"] = len(df)
                self.stats["original_columns"] = len(df.columns)
                self._log(
                    f"  Loaded {len(df):,} rows x {len(df.columns)} columns using {enc}"
                )
                return df

            except Exception as exc:
                last_error = exc
                continue

        raise ValueError(f"Failed to read CSV. Last error: {last_error}")

    @timer
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to lowercase, underscore-separated identifiers."""
        self._log("  Normalizing column names...")
        new_cols: List[str] = []
        seen: set = set()

        for i, col in enumerate(df.columns, start=1):
            col_str = str(col).strip() if col is not None else ""
            if not col_str or col_str.lower() == "nan":
                col_str = f"column_{i}"
            else:
                col_str = (
                    col_str.lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                    .replace(".", "_")
                )
                col_str = "".join(c for c in col_str if c.isalnum() or c == "_")
                if not col_str:
                    col_str = f"column_{i}"

            base, count = col_str, 1
            while col_str in seen:
                col_str = f"{base}_{count}"
                count += 1
            seen.add(col_str)
            new_cols.append(col_str)

        df.columns = new_cols
        self._log(f"  Normalized {len(new_cols)} column names")
        return df

    @timer
    def trim_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip leading and trailing whitespace from all string columns."""
        self._log("  Trimming whitespace...")
        str_cols = df.select_dtypes(include="object").columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
        return df

    @timer
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop fully duplicate rows."""
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        self.stats["rows_removed"] += removed
        if removed:
            self._log(f"  Removed {removed:,} duplicate rows")
        return df

    @timer
    def handle_missing(
        self, df: pd.DataFrame, fill_value: Optional[str], drop_na: bool
    ) -> pd.DataFrame:
        """Drop or fill rows with missing values."""
        if drop_na:
            before = len(df)
            df = df.dropna()
            removed = before - len(df)
            self.stats["rows_removed"] += removed
            if removed:
                self._log(f"  Dropped {removed:,} rows with missing values")
        elif fill_value is not None:
            df = df.fillna(fill_value)
            self._log(f"  Filled missing values with '{fill_value}'")
        return df

    @timer
    def select_columns(
        self,
        df: pd.DataFrame,
        keep: Optional[List[str]],
        drop: Optional[List[str]],
    ) -> pd.DataFrame:
        """Keep or drop named columns."""
        if keep:
            available = [c for c in keep if c in df.columns]
            missing = [c for c in keep if c not in df.columns]
            if missing:
                self._log(f"  WARNING - Columns not found and skipped: {', '.join(missing)}")
            df = df[available]
        elif drop:
            cols_to_drop = [c for c in drop if c in df.columns]
            df = df.drop(columns=cols_to_drop)
        return df

    @timer
    def optimize_types(self, df: pd.DataFrame, quick: bool) -> pd.DataFrame:
        """Downcast numeric types and categorize low-cardinality string columns."""
        if quick or len(df) < 1000:
            return df

        before_mb = df.memory_usage(deep=True).sum() / 1e6

        for col in df.select_dtypes(include="object").columns:
            ratio = df[col].nunique() / max(len(df), 1)
            if ratio < 0.5:
                df[col] = df[col].astype("category")

        for col in df.select_dtypes(include=np.number).columns:
            if pd.api.types.is_integer_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], downcast="integer", errors="ignore")
            elif pd.api.types.is_float_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], downcast="float", errors="ignore")

        after_mb = df.memory_usage(deep=True).sum() / 1e6
        self.stats["memory_saved_mb"] = round(max(before_mb - after_mb, 0.0), 2)
        return df

    @timer
    def split_column(
        self,
        df: pd.DataFrame,
        column: str,
        new_columns: List[str],
        delimiter: str,
    ) -> pd.DataFrame:
        """Split a column by a delimiter into multiple named columns."""
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found for splitting.")

        n = len(new_columns)
        splits = df[column].astype(str).str.split(delimiter, n=n - 1, expand=True)

        # Ensure splits has exactly n columns, padding with None if needed
        for i in range(n):
            df[new_columns[i]] = splits[i] if i in splits.columns else None

        return df

    @timer
    def add_columns(self, df: pd.DataFrame, add_map: Dict[str, str]) -> pd.DataFrame:
        """Add new columns as copies of existing columns."""
        for new_col, source_col in add_map.items():
            if source_col not in df.columns:
                raise ValueError(
                    f"Source column '{source_col}' not found; cannot create '{new_col}'."
                )
            df[new_col] = df[source_col]
        return df

    @timer
    def rename_columns(
        self, df: pd.DataFrame, rename_map: Dict[str, str]
    ) -> pd.DataFrame:
        """Rename columns using an old-to-new mapping."""
        missing = [old for old in rename_map if old not in df.columns]
        if missing:
            raise ValueError(
                f"Columns not found for renaming: {', '.join(missing)}"
            )
        return df.rename(columns=rename_map)

    @timer
    def save_file(
        self, df: pd.DataFrame, output: Path, encoding: str = "utf-8"
    ):
        """Write the cleaned DataFrame to a CSV file."""
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False, encoding=encoding)
        self._log(f"  Saved to: {output}")

    def clean(self, input_path: Path, output_path: Path, **opts) -> Dict:
        """Run the full cleaning pipeline and return stats."""
        self._log(f"Input:  {input_path}")
        self._log(f"Output: {output_path}")

        df = self.load_file(
            input_path,
            encoding=opts.get("encoding"),
            quick=opts.get("quick", False),
            chunk_size=opts.get("chunk_size"),
        )

        if opts.get("normalize"):
            df = self.normalize_columns(df)
        if opts.get("trim"):
            df = self.trim_whitespace(df)
        if opts.get("dedup"):
            df = self.remove_duplicates(df)

        df = self.handle_missing(df, opts.get("fill"), opts.get("drop_na", False))

        if opts.get("keep") or opts.get("drop"):
            df = self.select_columns(df, opts.get("keep"), opts.get("drop"))

        for split_args in opts.get("split") or []:
            column, new_cols, delim = split_args
            df = self.split_column(df, column, new_cols, delim)

        if opts.get("add"):
            df = self.add_columns(df, opts["add"])
        if opts.get("rename"):
            df = self.rename_columns(df, opts["rename"])

        df = self.optimize_types(df, opts.get("quick", False))
        self.save_file(df, output_path, encoding=opts.get("encoding", "utf-8"))

        end_time = time.time()
        self.stats.update(
            {
                "end_time": end_time,
                "elapsed_time": round(end_time - self.stats["start_time"], 3),
                "final_shape": df.shape,
                "success": True,
            }
        )
        return self.stats


def _parse_kv_list(pairs: List[str], flag: str) -> Dict[str, str]:
    """Parse a list of KEY=VALUE strings into a dict."""
    result = {}
    for pair in pairs:
        if "=" not in pair:
            print(
                f"WARNING: Ignoring malformed {flag} argument '{pair}' (expected KEY=VALUE)",
                file=sys.stderr,
            )
            continue
        k, _, v = pair.partition("=")
        result[k.strip()] = v.strip()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CleanR v{} - Professional CSV Cleaner".format(VERSION),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input CSV file path")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output CSV file path (default: <input>_clean.csv)",
    )
    parser.add_argument("-t", "--trim", action="store_true", help="Trim whitespace from string columns")
    parser.add_argument("-d", "--dedup", action="store_true", help="Remove duplicate rows")
    parser.add_argument("-n", "--normalize", action="store_true", help="Normalize column names to snake_case")
    parser.add_argument("-f", "--fill", metavar="VALUE", help="Fill missing values with VALUE")
    parser.add_argument("--drop-na", action="store_true", help="Drop rows that contain any missing value")
    parser.add_argument("--keep", metavar="COL1,COL2", help="Comma-separated list of columns to keep")
    parser.add_argument("--drop", metavar="COL1,COL2", help="Comma-separated list of columns to drop")
    parser.add_argument("--quick", action="store_true", help="Skip type optimization (faster for large files)")
    parser.add_argument("--chunk", type=int, metavar="N", help="Read file in chunks of N rows")
    parser.add_argument("--encoding", metavar="ENC", help="Force a specific file encoding (e.g. utf-8, latin1)")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument(
        "--split",
        nargs=3,
        action="append",
        metavar=("COLUMN", "NEW_COLUMNS", "DELIM"),
        help="Split COLUMN on DELIM into NEW_COLUMNS (comma-separated names). Repeatable.",
    )
    parser.add_argument(
        "--add",
        nargs="+",
        metavar="NEW=OLD",
        help="Add column(s) as copies of existing columns (NEW=OLD pairs).",
    )
    parser.add_argument(
        "--rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Rename column(s) (OLD=NEW pairs).",
    )

    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = (
        Path(args.output).resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}_clean{input_path.suffix}")
    )

    cleaner = CleanR(verbose=not args.quiet)

    opts: Dict = {
        "trim": args.trim,
        "dedup": args.dedup,
        "normalize": args.normalize,
        "fill": args.fill,
        "drop_na": args.drop_na,
        "quick": args.quick,
        "chunk_size": args.chunk or DEFAULT_CHUNK_SIZE,
        "encoding": args.encoding,
    }

    if args.keep:
        opts["keep"] = [c.strip() for c in args.keep.split(",") if c.strip()]
    if args.drop:
        opts["drop"] = [c.strip() for c in args.drop.split(",") if c.strip()]
    if args.split:
        opts["split"] = [
            (col, new_cols.split(","), delim) for col, new_cols, delim in args.split
        ]
    if args.add:
        opts["add"] = _parse_kv_list(args.add, "--add")
    if args.rename:
        opts["rename"] = _parse_kv_list(args.rename, "--rename")

    try:
        stats = cleaner.clean(input_path, output_path, **opts)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if stats["success"]:
        rows, cols = stats["final_shape"]
        elapsed = stats.get("elapsed_time", 0)
        print(
            f"Done. {output_path} | {rows:,} rows x {cols} cols | {elapsed:.2f}s"
        )
        if stats.get("memory_saved_mb"):
            print(f"Memory saved by type optimization: {stats['memory_saved_mb']} MB")
        return 0

    print("Cleaning failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
