![Conkas build](https://github.com/nveloso/conkas/workflows/build/badge.svg?branch=master)
![Conkas issues](https://img.shields.io/github/issues/nveloso/conkas?style=plastic)
![Conkas release](https://img.shields.io/github/v/release/nveloso/conkas?style=plastic)
![Conkas all releases](https://img.shields.io/github/downloads/nveloso/conkas/total?style=plastic)
![Conkas license](https://img.shields.io/github/license/nveloso/conkas?style=plastic)

![Docker build](https://github.com/nveloso/conkas/workflows/Docker%20build/badge.svg?branch=master)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/nveloso/conkas/latest?style=plastic)
![Docker Pulls](https://img.shields.io/docker/pulls/nveloso/conkas?style=plastic)

# Conkas

Conkas is a modular static analysis tool for Ethereum Virtual Machine (EVM) based on symbolic execution. It is capable of analysing Ethereum Smart Contracts written in Solidity or the compiled runtime bytecode. Being a modular tool means that anyone can add easily their custom modules to analyse specific vulnerabilities. It uses Z3 as the SMT Solver and [Rattle](https://github.com/crytic/rattle) as the Intermediate Representation (IR). However, to fit Conkas needs a modified version of Rattle is needed and that version can be found [here](https://github.com/nveloso/rattle). Conkas is part of my master's thesis.

## Usage

You can use Conkas via the Command-Line Interface (CLI).

If you have a Smart Contract written in Solidity and you want to search only for Reentrancy vulnerabilities you can type:
```bash
$ python3 conkas.py -vt reentrancy -s some_file.sol
```

If you have just the compiled runtime bytecode hex string and want to search for all types of vulnerabilities that Conkas provide you can type:
```bash
$ python3 conkas.py some_file.bin
```

## Dependencies

* [cbor2](https://pypi.org/project/cbor2/)
* [py-solc-x](https://pypi.org/project/py-solc-x/)
* [pycryptodome](https://pypi.org/project/pycryptodome/)
* [pyevmasm](https://pypi.org/project/pyevmasm/)
* [python3](https://www.python.org/downloads/)
* [solidity_parser](https://pypi.org/project/solidity-parser/)
* [z3-solver](https://pypi.org/project/z3-solver/)

You can use the requirements.txt file to install all dependencies via:
```bash
$ pip install -r requirements.txt
```

or create a python environment:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Detected Vulnerabilities

Conkas already have 5 modules to detect different categories of vulnerabilities. Conkas followed the [DASP Top 10](https://dasp.co/) when developing the modules. The 5 modules are:
* [Arithmetic](https://dasp.co/#item-3)
* [Reentrancy](https://dasp.co/#item-1)
* [Time Manipulation](https://dasp.co/#item-8)
* [Transaction Ordering Dependence](https://dasp.co/#item-7)
* [Unchecked Low-Level Calls](https://dasp.co/#item-4)

## Unit Tests

Conkas has several unit tests for testing the execution of EVM instructions. These tests can be found in __*tests/*__ folder.

# Results

[SmartBugs](https://github.com/smartbugs/smartbugs) was used to evaluate Conkas. The results can be found in the following tables. A vulnerability is considered true positive if the tool can give the category in which that vulnerability belongs and the line number in the source code of the Smart Contract with an interval of -5 to +5.

## Execution Time Stat

|  #  | Tool       | Avg. Execution Time | Total Execution Time |
| --- | ---------- | ------------------- | -------------------- |
|   1 | Conkas     | 0:00:32    | 1:14:37    |
|   2 | Honeybadger | 0:01:12    | 2:49:03    |
|   3 | Maian      | 0:03:47    | 8:52:25    |
|   4 | Manticore  | 0:12:53    | 1 day, 6:15:28 |
|   5 | Mythril    | 0:00:58    | 2:16:21    |
|   6 | Osiris     | 0:00:21    | 0:50:25    |
|   7 | Oyente     | 0:00:05    | 0:12:35    |
|   8 | Securify   | 0:02:06    | 4:56:13    |
|   9 | Slither    | 0:00:04    | 0:09:56    |
|  10 | Smartcheck | 0:00:15    | 0:35:23    |

Total: 2 days, 4:12:25

## Accuracy

|  Category           |   Conkas    | Honeybadger |    Maian    |  Manticore  |   Mythril   |   Osiris    |   Oyente    |  Securify   |   Slither   | Smartcheck  |    Total    |
| ------------------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| Access Control      |   0/24   0% |   0/24   0% |   0/24   0% |   5/24  21% |   4/24  17% |   0/24   0% |   0/24   0% |   1/24   4% |   6/24  25% |   2/24   8% |   8/24  33% |
| Arithmetic          |  19/23  83% |   0/23   0% |   0/23   0% |  13/23  57% |  16/23  70% |  13/23  57% |  18/23  78% |   0/23   0% |   0/23   0% |   1/23   4% |  22/23  96% |
| Denial Service      |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   0/14   0% |   1/14   7% |   1/14   7% |
| Front Running       |    2/7  29% |    0/7   0% |    0/7   0% |    0/7   0% |    2/7  29% |    0/7   0% |    2/7  29% |    2/7  29% |    0/7   0% |    0/7   0% |   2/ 7  29% |
| Reentrancy          |  30/34  88% |  19/34  56% |   0/34   0% |  15/34  44% |  25/34  74% |  21/34  62% |  28/34  82% |  14/34  41% |  33/34  97% |  30/34  88% |  33/34  97% |
| Time Manipulation   |    7/7 100% |    0/7   0% |    0/7   0% |    4/7  57% |    0/7   0% |    2/7  29% |    0/7   0% |    0/7   0% |    3/7  43% |    2/7  29% |   7/ 7 100% |
| Unchecked Low Calls |  62/75  83% |   0/75   0% |   0/75   0% |   9/75  12% |  60/75  80% |   0/75   0% |   0/75   0% |  50/75  67% |  51/75  68% |  61/75  81% |  70/75  93% |
| Other               |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |    0/5   0% |   0/ 5   0% |
| Total               | 120/224  54% | 19/224   8% |  0/224   0% | 46/224  21% | 107/224  48% | 36/224  16% | 48/224  21% | 67/224  30% | 93/224  42% | 97/224  43% | 143/224  64% |

# Add Custom Modules

To add custom modules you need to create a python file with one function that has the following signature:
```python
def vuln_x_analyse(traces: [Trace], find_all: bool) -> [Vulnerability]:
  pass
```
the variable *find_all* when have the value true means that the function should return all the vulnerabilities otherwise the function should return and stop when it finds only one vulnerability. You should put this file in __*vuln_finder/*__ folder. Then you need to modify the \_\_init\_\_.py in that folder and add to the *available_modules* object a line like this:
```python
from vuln_finder.vuln_name import vuln_x_analyse

available_modules = {
  ...,
  'vuln_name': vuln_x_analyse
}
```
'*vuln_name*' should be the name of the vulnerability that you detect and '*vuln_x_analyse*' should be the name of the function that makes the analysis.

# License

Conkas is licensed and distributed under the AGPL-3.0 (AGPLv3) License
