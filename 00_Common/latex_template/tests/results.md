# Extra checks (tests/run_tests.py)

## 1. Line breaking against Word

| set | lines Word | lines LaTeX | identical lines | identical and on the same page | pages W/L |
|---|---:|---:|---:|---:|---:|
| linebreak_fit | 529 | 529 | 529 (100.0 %) | 529 | 13/13 |
| linebreak_holdout | 468 | 468 | 464 (99.1 %) | 464 | 12/12 |

First line of each differing block:

- linebreak_holdout: Word `eo, sit sodales 1 non, auctor sit lacus 5 2 metus eu, turpis` / LaTeX `sit sodales 1 non, auctor sit lacus 5 2 metus eu, turpis mi,`
- linebreak_holdout: Word ` egestas 1.5 venenatis sagittis eget ex. dapibus . nisl amet` / LaTeX `tas 1.5 venenatis sagittis eget ex. dapibus . nisl amet odio`

## 2. Reference list, table and figure against the EASA report

- References [1]-[5] (EASA page 8): 12 of 12 printed lines identical; max baseline difference 0.00 bp (rounded baselines).
- Table 1 rules, bp below the caption baseline: Word [7.08, 19.8, 142.1], LaTeX [7.13, 19.95, 141.9]
- Table 1 first-column baselines, bp below the caption baseline: Word [16.92, 28.56, 48.84, 69.12, 80.28, 109.68, 129.96], LaTeX [16.83, 28.45, 48.73, 69.02, 80.16, 109.59, 129.88]
- Figure: picture bottom to caption baseline: Word 11.9 bp, LaTeX 11.91 bp
