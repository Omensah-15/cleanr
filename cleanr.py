#!/usr/bin/env python3
"""
CleanR - Professional CSV Cleaner
Fast, memory-efficient, and robust CSV processing.
"""

import sys
import os
import time
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np
import yaml

warnings.filterwarnings("ignore")

SUPPORTED_ENCODINGS = ["utf-8", "latin1", "iso-8859-1", "cp1252", "utf-16", "utf-8-sig"]
DEFAULT_CHUNK_SIZE = 100_000
VERSION = "1.0.0"


class CleanR:
    """Main cleaning engine."""

    def __init__(self, verbose: bool = True):
        self.stats = {
            "start_time": time.time(),
            "rows_processed": 0,
            "rows_removed": 0,
            "memory_saved_mb": 0,
            "success": False,
        }
        self.verbose = verbose

    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    @staticmethod
    def timer(func):
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            elapsed = time.time() - start
            if elapsed > 0.1 and self.verbose:
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
        if not filepath.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")

        encodings = [encoding] if encoding else SUPPORTED_ENCODINGS
        last_error = None

        for enc in encodings:
            try:
                self._log(f"  Trying encoding: {enc}")
                if chunk_size and chunk_size > 0:
                    chunks = []
                    for chunk in pd.read_csv(
                        filepath,
                        encoding=enc,
                        chunksize=chunk_size,
                        dtype=str if quick else None,
                        low_memory=False,
                        on_bad_lines='skip'
                    ):
                        chunks.append(chunk)
                    if chunks:
                        df = pd.concat(chunks, ignore_index=True)
                    else:
                        raise ValueError("No data loaded from CSV")
                else:
                    df = pd.read_csv(
                        filepath,
                        encoding=enc,
                        dtype=str if quick else None,
                        low_memory=False,
                        on_bad_lines='skip'
                    )

                self.stats["rows_processed"] = len(df)
                self.stats["original_columns"] = len(df.columns)
                self._log(f"  ✓ Loaded {len(df):,} rows, {len(df.columns)} columns using {enc}")
                return df

            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        error_msg = f"Failed to read CSV with supported encodings. Last error: {last_error}"
        raise ValueError(error_msg)

    @timer
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log("  Normalizing column names...")
        new_cols = []
        seen = set()

        for i, col in enumerate(df.columns, start=1):
            if pd.isna(col):
                col = f"column_{i}"
            else:
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
        self._log(f"  ✓ Normalized {len(new_cols)} columns")
        return df

    @timer
    def trim_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log("  Trimming whitespace...")
        cols = df.select_dtypes(include="object").columns
        for col in cols:
            df[col] = df[col].astype(str).str.strip()
        self._log(f"  ✓ Trimmed {len(cols)} columns")
        return df

    @timer
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        self._log("  Removing duplicates...")
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        self.stats["rows_removed"] += removed
        if removed > 0:
            self._log(f"  ✓ Removed {removed:,} duplicate rows")
        else:
            self._log("  ✓ No duplicates found")
        return df

    @timer
    def handle_missing(
        self,
        df: pd.DataFrame,
        fill_value: Optional[str],
        drop_na: bool,
    ) -> pd.DataFrame:
        if drop_na:
            self._log("  Dropping rows with missing values...")
            before = len(df)
            df = df.dropna()
            removed = before - len(df)
            self.stats["rows_removed"] += removed
            if removed > 0:
                self._log(f"  ✓ Removed {removed:,} rows with missing values")
        elif fill_value is not None:
            self._log(f"  Filling missing values with: '{fill_value}'")
            df = df.fillna(fill_value)
            self._log("  ✓ Filled missing values")
        return df

    @timer
    def select_columns(
        self,
        df: pd.DataFrame,
        keep: Optional[List[str]],
        drop: Optional[List[str]],
    ) -> pd.DataFrame:
        if keep:
            available_cols = [c for c in keep if c in df.columns]
            missing_cols = [c for c in keep if c not in df.columns]
            if missing_cols and self.verbose:
                print(f"  ⚠ Warning: Columns not found: {', '.join(missing_cols)}")
            df = df[available_cols]
            self._log(f"  ✓ Kept {len(available_cols)} columns")
        elif drop:
            cols_to_drop = [c for c in drop if c in df.columns]
            missing_cols = [c for c in drop if c not in df.columns]
            if missing_cols and self.verbose:
                print(f"  ⚠ Warning: Columns not found: {', '.join(missing_cols)}")
            df = df.drop(columns=cols_to_drop)
            self._log(f"  ✓ Dropped {len(cols_to_drop)} columns")
        return df

    @timer
    def optimize_types(self, df: pd.DataFrame, quick: bool) -> pd.DataFrame:
        if quick or len(df) < 1000:
            return df

        self._log("  Optimizing data types...")
        before = df.memory_usage(deep=True).sum() / 1e6

        # Convert object columns with low cardinality to category
        for col in df.select_dtypes(include="object").columns:
            try:
                unique_ratio = df[col].nunique(dropna=True) / max(len(df), 1)
                if unique_ratio < 0.5:
                    df[col] = df[col].astype("category")
            except:
                continue

        # Convert numeric columns to appropriate types
        for col in df.select_dtypes(include=[np.number]).columns:
            try:
                col_min = df[col].min()
                col_max = df[col].max()
                
                if pd.api.types.is_integer_dtype(df[col]):
                    if col_min >= 0:
                        if col_max < 256:
                            df[col] = pd.to_numeric(df[col], downcast='unsigned')
                        elif col_max < 65536:
                            df[col] = pd.to_numeric(df[col], downcast='unsigned')
                else:
                    df[col] = pd.to_numeric(df[col], downcast='float')
            except:
                continue

        after = df.memory_usage(deep=True).sum() / 1e6
        saved = before - after
        if saved > 1:
            self.stats["memory_saved_mb"] = round(saved, 2)
            self._log(f"  ✓ Saved {saved:.1f} MB of memory")

        return df

    def load_profile(self, name: str, directory: Path) -> Dict:
        """Load cleaning profile from YAML file."""
        path = directory / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found at {path}")

        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    @timer
    def save_file(self, df: pd.DataFrame, output: Path, config: Dict):
        """Save DataFrame to CSV file."""
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            
            save_config = {
                'index': False,
                'encoding': config.get("encoding", "utf-8"),
            }
            
            if config.get("float_precision"):
                save_config['float_format'] = f"%.{config['float_precision']}f"
            
            df.to_csv(output, **save_config)
            self._log(f"  ✓ Saved to: {output}")
            self.stats["output_file"] = str(output)
        except Exception as e:
            raise IOError(f"Failed to save file: {e}")

    def clean(self, input_path: Path, output_path: Path, **opts) -> Dict:
        """Main cleaning pipeline."""
        self._log(f"Input:  {input_path}")
        self._log(f"Output: {output_path}")
        
        try:
            # Load file
            df = self.load_file(
                input_path,
                encoding=opts.get("encoding"),
                quick=opts.get("quick", False),
                chunk_size=opts.get("chunk_size"),
            )

            # Apply cleaning operations
            if opts.get("normalize", False):
                df = self.normalize_columns(df)

            if opts.get("trim", False):
                df = self.trim_whitespace(df)

            if opts.get("dedup", False):
                df = self.remove_duplicates(df)

            df = self.handle_missing(df, opts.get("fill"), opts.get("drop_na", False))
            
            if opts.get("keep") or opts.get("drop"):
                df = self.select_columns(df, opts.get("keep"), opts.get("drop"))
            
            df = self.optimize_types(df, opts.get("quick", False))

            # Save result
            self.save_file(df, output_path, opts)
            
            # Update statistics
            self.stats["end_time"] = time.time()
            self.stats["elapsed_time"] = self.stats["end_time"] - self.stats["start_time"]
            self.stats["final_shape"] = df.shape
            self.stats["success"] = True
            
            # Print summary
            self._log("\n" + "="*50)
            self._log("CLEANING SUMMARY")
            self._log("="*50)
            self._log(f"Original: {self.stats['rows_processed']:,} rows × {self.stats.get('original_columns', '?')} cols")
            self._log(f"Final:    {df.shape[0]:,} rows × {df.shape[1]} cols")
            self._log(f"Removed:  {self.stats['rows_removed']:,} rows total")
            if self.stats.get('memory_saved_mb', 0) > 0:
                self._log(f"Memory:   Saved {self.stats['memory_saved_mb']} MB")
            self._log(f"Time:     {self.stats['elapsed_time']:.2f} seconds")
            self._log("="*50)
            
            return self.stats
            
        except Exception as e:
            self.stats["error"] = str(e)
            self.stats["success"] = False
            if self.verbose:
                print(f"\n Error: {e}", file=sys.stderr)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="CleanR - Professional CSV Cleaner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cleanr input.csv output.csv                    # Basic cleaning
  cleanr data.csv --trim --dedup                 # Trim and remove duplicates
  cleanr large.csv --quick --chunk 50000         # Process large files
  cleanr messy.csv --normalize --fill "NA"       # Normalize and fill NA
  cleanr sales.csv --keep "date,amount,name"     # Keep specific columns

For more details, visit: https://github.com/Omensah-15/cleanr
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"CleanR {VERSION}"
    )
    
    parser.add_argument(
        "input",
        help="Input CSV file path"
    )
    
    parser.add_argument(
        "output",
        nargs="?",
        help="Output CSV file path (optional, defaults to input_clean.csv)"
    )
    
    # Cleaning options
    parser.add_argument(
        "-t", "--trim",
        action="store_true",
        help="Trim whitespace from all string columns"
    )
    
    parser.add_argument(
        "-d", "--dedup",
        action="store_true",
        help="Remove duplicate rows"
    )
    
    parser.add_argument(
        "-n", "--normalize",
        action="store_true",
        help="Normalize column names (lowercase, underscores)"
    )
    
    parser.add_argument(
        "-f", "--fill",
        metavar="VALUE",
        help="Fill missing values with specified value"
    )
    
    parser.add_argument(
        "--drop-na",
        action="store_true",
        help="Drop rows with any missing values"
    )
    
    parser.add_argument(
        "--keep",
        metavar="COLUMNS",
        help="Keep only specified columns (comma-separated)"
    )
    
    parser.add_argument(
        "--drop",
        metavar="COLUMNS",
        help="Drop specified columns (comma-separated)"
    )
    
    # Performance options
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (skip type optimization for faster processing)"
    )
    
    parser.add_argument(
        "--chunk",
        type=int,
        metavar="SIZE",
        help=f"Process in chunks (default: {DEFAULT_CHUNK_SIZE})"
    )
    
    parser.add_argument(
        "--encoding",
        help=f"File encoding (default: auto-detect from {', '.join(SUPPORTED_ENCODINGS[:3])}...)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode (minimal output)"
    )
    
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="Use cleaning profile from YAML file"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.fill and args.drop_na:
        print("Error: Cannot use both --fill and --drop-na options together", file=sys.stderr)
        return 1
    
    if args.keep and args.drop:
        print("Error: Cannot use both --keep and --drop options together", file=sys.stderr)
        return 1
    
    # Process file paths
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        # Default output: input_clean.csv in same directory
        output_path = input_path.with_name(f"{input_path.stem}_clean{input_path.suffix}")
    
    # Check if output file already exists
    if output_path.exists() and output_path != input_path:
        print(f"Warning: Output file already exists: {output_path}", file=sys.stderr)
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Operation cancelled", file=sys.stderr)
            return 0
    
    # Initialize cleaner
    cleaner = CleanR(verbose=not args.quiet)
    
    try:
        # Prepare options
        clean_opts = {
            "trim": args.trim,
            "dedup": args.dedup,
            "normalize": args.normalize,
            "fill": args.fill,
            "drop_na": args.drop_na,
            "quick": args.quick,
            "chunk_size": args.chunk or DEFAULT_CHUNK_SIZE,
            "encoding": args.encoding,
        }
        
        # Process keep/drop columns
        if args.keep:
            clean_opts["keep"] = [col.strip() for col in args.keep.split(",")]
        if args.drop:
            clean_opts["drop"] = [col.strip() for col in args.drop.split(",")]
        
        # Load profile if specified
        if args.profile:
            try:
                profile_dir = Path.home() / ".cleanr" / "profiles"
                profile_config = cleaner.load_profile(args.profile, profile_dir)
                clean_opts.update(profile_config)
            except Exception as e:
                print(f"Warning: Could not load profile '{args.profile}': {e}", file=sys.stderr)
        
        # Run cleaning
        stats = cleaner.clean(
            input_path=input_path,
            output_path=output_path,
            **clean_opts
        )
        
        if stats["success"]:
            if not args.quiet:
                print(f"\n Cleaning completed successfully!")
                print(f"   Output: {output_path}")
            return 0
        else:
            print(f"\n Cleaning failed: {stats.get('error', 'Unknown error')}", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠ Operation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n Error during cleaning: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1



if __name__ == "__main__":
    sys.exit(main())
