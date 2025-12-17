# CleanR - CSV Cleaner

Fast, memory-efficient Python tool to clean CSVs: trim whitespace, remove duplicates, normalize columns, handle missing data, and select/drop columns.

---
## Features:
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

## Usage

```bash
# Basic cleaning
cleanr messy_data.csv

# Full cleaning pipeline
cleanr input.csv output.csv \
  --trim --dedup --normalize \
  --fill "NULL" --keep name,email,date

# For large files
cleanr bigfile.csv --quick --chunk 50000
```

## Install

1. Download cleanr.py
2. Make executable: chmod +x cleanr.py
3. Add alias: alias cleanr='python cleanr.py'
## Demo:
[messy_data.csv]() to [clean_data.csv]() in secs
#### script demo:

## License: MIT
