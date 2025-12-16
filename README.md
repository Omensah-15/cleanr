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
| Flag | What it does |
|------|--------------|
| `--trim`       | Trim spaces |
| `--dedup`      | Remove duplicates |
| `--normalize`  | Clean column names |
| `--fill VALUE` | Fill missing values |
| `--drop-na`    | Drop rows with NA |
| `--keep COLS`  | Keep only these columns |
| `--drop COLS`  | Drop these columns |
| `--quick`      | Fast mode (all strings) |
| `--chunk SIZE` | Process in chunks |
| `--encoding`   | Force encoding |



Output

· Defaults to <original>_clean.csv in the same folder.
