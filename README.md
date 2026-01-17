# CleanR - CSV Cleaner

**One command to clean any CSV file.** Remove duplicates, fix formatting, normalize columns, and process large files instantly.

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

## Demo:
![image alt](https://github.com/Omensah-15/cleanr/blob/0056912278c287d77d71effebfdcca59e5aa17ca/demo/linux_screenshot.png)
- Before: [messy_data.csv](https://github.com/Omensah-15/cleanr/blob/main/examples/messy_data.csv)
- After: [clean_data.csv](https://github.com/Omensah-15/cleanr/blob/main/examples/clean_data.csv)

## Installation

### Step 1: Install Python
Download and install Python from [python.org](https://www.python.org/downloads/).  
**Important:** During installation, check **"Add Python to PATH"**.

### Step 2: Install Dependencies
Open terminal and run:
```powershell
python -m pip install pandas pyyaml numpy
```
### Step 3: Install CleanR
#### For Windows PowerShell:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py" -OutFile "$env:USERPROFILE\cleanr.py"
New-Item -ItemType Directory -Force -Path (Split-Path $PROFILE)
"function cleanr { python `"`$env:USERPROFILE\cleanr.py`" `$args }" | Add-Content -Path $PROFILE
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```
#### For Linux/Mac/Git Bash:
```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py -o ~/cleanr.py
echo "alias cleanr='python ~/cleanr.py'" >> ~/.bashrc
source ~/.bashrc
```
#### Close and reopen the terminal. Then use: 
```bash
cleanr --help
```
## Usage & Examples:
```cmd
# Standard cleanup: trim spaces, remove duplicates, fix column names
cleanr messy.csv cleaned.csv --trim --dedup --normalize

# Handle missing data  
cleanr data.csv --fill "Unknown"

# Process large files in chunks to avoid memory issues
cleanr huge_logs.csv clean_logs.csv --chunk 100000 --quick
```

## License: MIT

## 👨‍💻 Author

**Developed by Mensah Obed**
[Email](mailto:heavenzlebron7@gmail.com) 
[LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
