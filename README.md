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


## One-Command Installation

```bash
# Install and test CleanR in one line:
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py | python3 - --help

# Or for permanent installation:
curl -sL https://raw.githubusercontent.com/Omensah-15/cleanr/main/cleanr.py -o ~/cleanr.py && echo "alias cleanr='python ~/cleanr.py'" >> ~/.bashrc && pip install pandas pyyaml numpy

## Install

1. Download cleanr.py
2. Make executable: chmod +x cleanr.py
3. Add alias: alias cleanr='python cleanr.py'
```

## License: MIT

## 👨‍💻 Author

**Developed by Mensah Obed**
[Email](mailto:heavenzlebron7@gmail.com) 
[LinkedIn](https://www.linkedin.com/in/obed-mensah-87001237b)
