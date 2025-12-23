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

### For Windows CMD:
```cmd
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py').read().decode('utf-8'))" --help
```
### For Linux/Mac/Git Bash:
```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py | python3 - --help
```
### Permanent install (Linux/Mac):
```bash
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py -o ~/cleanr.py && echo "alias cleanr='python ~/cleanr.py'" >> ~/.bashrc && pip install pandas pyyaml numpy
```
## License: MIT

## 👨‍💻 Author

**Developed by Mensah Obed**
[Email](mailto:heavenzlebron7@gmail.com) 
[LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
