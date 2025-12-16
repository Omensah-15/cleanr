#!/usr/bin/env python3
"""
CleanR - Professional CSV Cleaner
Fast, memory-efficient, and robust CSV processing.
"""

import sys
import time
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
import yaml

warnings.filterwarnings("ignore")

SUPPORTED_ENCODINGS = ["utf-8", "latin1", "iso-8859-1", "cp1252", "utf-16"]
DEFAULT_CHUNK_SIZE = 100_000


class CleanR:
    """Main cleaning engine."""

    def __init__(self):
        self.stats = {
            "start_time": time.time(),
            "rows_processed": 0,
            "rows_removed": 0,
            "memory_saved_mb": 0,
            "success": False,
        }

    @staticmethod
    def timer(func):
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            elapsed = time.time() - start
            if elapsed > 0.1:
                print(f"  {func.__name__.replace('_', ' ').title()}: {elapsed:.2f}s")
            return result

        return wrapper

    @timer
    def load_file(
        self,
        filepath: Path,
        encoding: Optional[str] = None,
        quick: bool = False,
        chunk_size: Optional[int] = None,
    ) -> pd.DataFrame:
        """Load CSV with encoding fallback."""
        encodings = [encoding] if encoding else SUPPORTED_ENCODINGS

        for enc in encodings:
            try:
                if chunk_size:
                    chunks = pd.read_csv(
                        filepath,
                        encoding=enc,
                        chunksize=chunk_size,
                        dtype=str if quick else None,
                        low_memory=False,
                    )
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    df = pd.read_csv(
                        filepath,
                        encoding=enc,
                        dtype=str if quick else None,
                        low_memory=False,
                    )

                self.stats["rows_processed"] = len(df)
                print(f"  Loaded using encoding: {enc}")
                return df

            except UnicodeDecodeError:
                continue

        raise ValueError("Failed to read CSV with supported encodings")

    @timer
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        new_cols = []
        seen = set()

        for i, col in enumerate(df.columns, start=1):
            col = str(col).strip().lower()
            col = col.replace(" ", "_").replace("-", "_").replace(".", "_")
            col = "".join(c for c in col if c.isalnum() or c == "_")
            if not col:
                col = f"column_{i}"

            base = col
            count = 1
            while col in seen:
                col = f"{base}_{count}"
                count += 1

            seen.add(col)
            new_cols.append(col)

        df.columns = new_cols
        return df

    @timer
    def trim_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = df.select_dtypes(include="object").columns
        for col in cols:
            df[col] = df[col].astype(str).str.strip()
        return df

    @timer
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        self.stats["rows_removed"] += removed
        return df

    @timer
    def handle_missing(
        self,
        df: pd.DataFrame,
        fill_value: Optional[str],
        drop_na: bool,
    ) -> pd.DataFrame:
        if drop_na:
            before = len(df)
            df = df.dropna()
            self.stats["rows_removed"] += before - len(df)
        elif fill_value is not None:
            df = df.fillna(fill_value)
        return df

    @timer
    def select_columns(
        self,
        df: pd.DataFrame,
        keep: Optional[List[str]],
        drop: Optional[List[str]],
    ) -> pd.DataFrame:
        if keep:
            df = df[[c for c in keep if c in df.columns]]
        elif drop:
            df = df.drop(columns=[c for c in drop if c in df.columns])
        return df

    @timer
    def optimize_types(self, df: pd.DataFrame, quick: bool) -> pd.DataFrame:
        if quick or len(df) < 1000:
            return df

        before = df.memory_usage(deep=True).sum() / 1e6

        for col in df.select_dtypes(include="object"):
            unique_ratio = df[col].nunique(dropna=True) / max(len(df), 1)
            if unique_ratio < 0.5:
                df[col] = df[col].astype("category")

        after = df.memory_usage(deep=True).sum() / 1e6
        saved = before - after
        if saved > 1:
            self.stats["memory_saved_mb"] = round(saved, 2)

        return df

    def load_profile(self, name: str, directory: Path) -> Dict:
        path = directory / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found")

        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    @timer
    def save_file(self, df: pd.DataFrame, output: Path, config: Dict):
        output.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(
            output,
            index=False,
            encoding=config.get("encoding", "utf-8"),
            float_format=(
                f"%.{config['float_precision']}f"
                if config.get("float_precision")
                else None
            ),
        )

    def clean(self, input_path: Path, output_path: Path, **opts) -> Dict:
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

        df = self.handle_missing(df, opts.get("fill"), opts.get("drop_na"))
        df = self.select_columns(df, opts.get("keep"), opts.get("drop"))
        df = self.optimize_types(df, opts.get("quick", False))

        self.save_file(df, output_path, {})
        self.stats["end_time"] = time.time()
        self.stats["elapsed_time"] = self.stats["end_time"] - self.stats["start_time"]
        self.stats["final_shape"] = df.shape
        self.stats["success"] = True

        return self.stats


def main():
    parser = argparse.ArgumentParser(description="CleanR CSV Cleaner")

    parser.add_argument("input")
    parser.add_argument("output", nargs="?")

    parser.add_argument("-t", "--trim", action="store_true")
    parser.add_argument("-d", "--dedup", action="store_true")
    parser.add_argument("-n", "--normalize", action="store_true")
    parser.add_argument("-f", "--fill")
    parser.add_argument("--drop-na", action="store_true")
    parser.add_argument("--keep")
    parser.add_argument("--drop")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--chunk", type=int)
    parser.add_argument("--encoding")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = (
        Path(args.output)
        if args.output
        else input_path.with_name(f"{input_path.stem}_clean{input_path.suffix}")
    )

    cleaner = CleanR()

    cleaner.clean(
        input_path=input_path,
        output_path=output_path,
        trim=args.trim,
        dedup=args.dedup,
        normalize=args.normalize,
        fill=args.fill,
        drop_na=args.drop_na,
        keep=args.keep.split(",") if args.keep else None,
        drop=args.drop.split(",") if args.drop else None,
        quick=args.quick,
        chunk_size=args.chunk,
        encoding=args.encoding,
    )

    print("Cleaning complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
