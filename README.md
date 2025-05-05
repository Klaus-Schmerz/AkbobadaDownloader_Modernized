# AkbobadaDownloader

    

> **Note on Project Migration**  💡
>
> This version contains update that differ significantly from the previous codebase. You can still find the previous codebase [**here**](https://github.com/Klaus-Schmerz/AkbobadaDownloader).
>
> This README covers the **refactored & revamped** version now maintained in this repository.

---

## ✨ Overview

Light, Fast, Multi-Account supporting Akbobada Downloader

## 🚀 Key Features

* **Light :** For HTTP Connections, Use only `requests` not `Selenium` therefore requires very little resources.
* **Fast :** Ensure faster speeds than when using `multiprocessing` because of handling scraping and downloading asynchronously.
* **Multi-Accounting Support :** Just by modifying the configuration file, You can download multiple accounts at once.
* **Memory :** Memorizes last score by accounts so that next time you run it, it downloads until the last score.
* **Adjustable Asynchronous Processing Count :** Can set the number of asynchronous processes so that it can cope with various network situations and computing performance

## ⚡ Quick Start

Clone this repository

```bash
$ git clone https://github.com/Klaus-Schmerz/AkbobadaDownloader_Modernized.git
$ cd AkbobadaDownloader_Modernized
```

Before run the code, Please update `config.toml` appropreately to your conditions by [this](#configuration-file)

Run the code
```bash
$ python run.py
```

## ⚙️ Arguments

| Variable           | Type | Default | Description                                                          |
| ------------------ | ---- | ------- | -------------------------------------------------------------------- |
| `-r`, `--recovery` | None |         | Download the entire score list regardless of the last download score |
| `-b`, `--batch`    | int  | 100     | Amount to be shared when there is a large amount of score            |
| `-w`, `--workers`  | int  | 10      | Number of asynchronous processes                                     |

### For example:
```bash
$ python run.py -r
$ python run.py -b 100
$ python run.py -r -w 10
```

## ⚙️ Configuration File

The format of the configuration file is `toml`.
You have to locate the configuration file at the same directory of `run.py` and name of the file must be `config.toml`.

* **[[accounts]] :** The information about your Akbobada accounts. Write sevel times when you want to download multiple accounts.
                     Keys are consisted of `id` and `pw`, Values are `str`
* **[download] :** Options for download settings. For now, output directory is an only option. The scores are stored under the folder with the part name under the folder name you specied.
                   Key is `outdir`, Value is `str`

## 🧩 Directory Structure

```text
└── AkbobadaDownloader_Modernized/
    ├── history/
    │   ├   id1.pkl
    │   ├   id2.pkl
    │   └   ...                       # Information of last score
    ├── scores/
    │   ├   건반/
    │   ├   기타1,2/
    │   └   베이스/                   # Actual score files
    ├── workers/
    ├   akbo.py
    ├   akbo_history.py
    ├   akbo_ticket.py
    ├   akbo_utils.py
    ├   config.toml                   # Configuration file
    └   run.py                        # Entry file
```
