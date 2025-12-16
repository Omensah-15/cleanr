# CleanR - CSV Cleaner

Fast, memory-efficient Python tool to clean CSVs: trim whitespace, remove duplicates, normalize columns, handle missing data, and select/drop columns.

---

## Quick Start

```bash
python3 y.py <input.csv> [output.csv] [options]# cleanr
```
## Examples:
```bash
# Basic cleaning
python3 y.py ./data/sales.csv

# With options
python3 y.py ./data/sales.csv ./output/sales_clean.csv \
  --trim --dedup --normalize --fill "NA" --keep name,email
```
Output

· Defaults to <original>_clean.csv in the same folder.
