# CleanR

CleanR is a fast, memory-efficient, command-line CSV cleaner designed for data analysts, engineers, and anyone who wants to clean and prepare CSV data in seconds. Stop wasting time hunting through spreadsheet menus — CleanR automates everything with one command.

---

## Demo
<div align="center">
  <img src="https://github.com/Omensah-15/cleanr/blob/425bdb64ff60d45a1e4d802225476e4a60b34308/demo/demo2.gif" alt="Demo" width="800">
</div>

- Before: [messy_data.csv](https://github.com/Omensah-15/cleanr/blob/main/demo/examples/messy_data.csv)
- After: [clean_data.csv](https://github.com/Omensah-15/cleanr/blob/main/demo/examples/clean_data.csv)

---

## Installation

**Requirements:** Python 3.7+ with pandas and numpy.

```bash
pip install pandas numpy
```

**Linux / Mac / Git Bash**

```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py -o ~/cleanr.py
echo "alias cleanr='python ~/cleanr.py'" >> ~/.bashrc
source ~/.bashrc
```

**Windows PowerShell**

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py" -OutFile "$env:USERPROFILE\cleanr.py"
New-Item -ItemType Directory -Force -Path (Split-Path $PROFILE)
"function cleanr { python `"`$env:USERPROFILE\cleanr.py`" `$args }" | Add-Content -Path $PROFILE
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

Reopen your terminal, then verify with:

```bash
cleanr --help
```

---

## Usage

```bash
cleanr input.csv output.csv [options]
```

If no output path is given, the result is saved as `input_clean.csv`.

---

## Options

| Flag | Description |
|------|-------------|
| `-t, --trim` | Strip whitespace from string columns |
| `-d, --dedup` | Remove duplicate rows |
| `-n, --normalize` | Normalize column names to snake_case |
| `-f, --fill VALUE` | Fill missing values with VALUE |
| `--drop-na` | Drop rows that contain any missing value |
| `--keep COL1,COL2` | Keep only the specified columns |
| `--drop COL1,COL2` | Drop the specified columns |
| `--rename OLD=NEW` | Rename a column |
| `--add NEW=OLD` | Add a column as a copy of an existing one |
| `--split COL NEW1,NEW2 DELIM` | Split a column by a delimiter |
| `--quick` | Skip type optimization (faster for large files) |
| `--chunk N` | Read file in chunks of N rows |
| `--encoding ENC` | Force a specific file encoding |
| `--quiet` | Suppress progress output |

---

## Examples

```bash
# Standard cleanup
cleanr messy.csv cleaned.csv --trim --dedup --normalize

# Fill missing values
cleanr data.csv output.csv --fill "Unknown"

# Drop rows with any missing data
cleanr data.csv output.csv --drop-na

# Process a large file in chunks
cleanr huge_logs.csv clean_logs.csv --chunk 100000 --quick

# Split a full name column into first/last:
cleanr input.csv output.csv --split full_name first,last " "

# Keep only specific columns
cleanr data.csv output.csv --keep id,name,email

# Rename a column
cleanr data.csv output.csv --rename old_name=new_name

#Full pipeline in one line
cleanr input.csv output.csv --trim --dedup --normalize --drop-na --split full_name first,last " " --add username=email --rename old_email:new_email --quick
```

---

## License

MIT

---

## Author

Mensah Obed — [Email](mailto:heavenzlebron7@gmail.com) | [LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
EOF
