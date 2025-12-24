# CleanR - CSV Cleaner

**One command to clean any CSV file.** Remove duplicates, fix formatting, normalize columns, and process large files—instantly.

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


## Quick Start

**Copy and paste this command in your terminal to install and run CleanR:**

### For Windows PowerShell:
```powershell
# CleanR PowerShell Installation
# Run this once to install permanently

# 1. Download the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py" -OutFile "$env:USERPROFILE\cleanr.py"

# 2. Create profile directory if it doesn't exist
New-Item -ItemType Directory -Force -Path (Split-Path $PROFILE)

# 3. Add cleanr function to profile
"function cleanr { python `"`$env:USERPROFILE\cleanr.py`" `$args }" | Add-Content -Path $PROFILE

# 4. Ensure profile loads on startup (registry fix)
$registryPath = "HKCU:\Software\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell"
$command = ". '$($PROFILE)'"
Set-ItemProperty -Path $registryPath -Name "StartupScript" -Value $command -Type String -Force

# 5. Set execution policy (if needed)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

Write-Host "CleanR installed! Close and reopen PowerShell, then use: cleanr --help"
```
### For Linux/Mac/Git Bash:
```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py | python3 - --help
```
## Examples:
```cmd
# Clean a file
cleanr messy.csv clean.csv --trim --dedup --normalize

# Handle missing data  
cleanr data.csv --fill "Unknown"

# Large files
cleanr large.csv --quick --chunk 100000
```
## Dependencies:
```bash
pip install pandas pyyaml numpy
```
## License: MIT

## 👨‍💻 Author

**Developed by Mensah Obed**
[Email](mailto:heavenzlebron7@gmail.com) 
[LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
