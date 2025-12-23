# CleanR - CSV Cleaner

**One-line CSV cleaning.** Trim, deduplicate, normalize, and process large files instantly.

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


## One-Command Installation

### For Windows PowerShell:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py -o $env:USERPROFILE\cleanr.py
function cleanr { python "$env:USERPROFILE\cleanr.py" $args }
cleanr --help
```
### For Linux/Mac/Git Bash:
```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py | python3 - --help
```

## License: MIT

## 👨‍💻 Author

**Developed by Mensah Obed**
[Email](mailto:heavenzlebron7@gmail.com) 
[LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
