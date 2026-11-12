# Causal Analysis of Deal or No Deal

MSML610, Fall 2026, Group 28: Stuti Patel and Riya Puri.

This project studies how game state, banker offers, and previous prize draws
relate to contestants' Deal/No Deal decisions. The implemented Python pipeline
loads the Australian ZBW data, selects games, reconstructs prize boards,
builds offer-level features, and fits a baseline logit.

The model estimates associations. It does not establish a causal effect.

## Data and verified counts

The primary dataset accompanies de Roos and Sarafidis (2010),
*Decision Making Under Risk in Deal or No Deal*. Each raw record describes
one round. The file has 20 whitespace-separated fields and uses `-999` for
missing values.

| Stage | Rows | Games |
|---|---:|---:|
| Raw ZBW data | 4,664 | 424 |
| Cleaned Series 2.00, 3.00, 3.10 | 3,421 | 311 |
| Reconstructed clean games | 3,410 | 310 |
| Offer-level features | 2,136 | 291 |
| Model sample with defined luck | 1,845 | 291 |

- Cleaning removes entire special-show games. Unknown special-show flags
  count as clean under the current sample policy.
- Show 336 fails reconstruction in the cleaned sample.
- The other 19 reconstructed games absent from the offer sample have no
  recorded banker offers.
- Reconstructing the full raw dataset succeeds for 422 games and 4,642 rows.
  Shows 336 and 1003 fail under the configured boards.
- The secondary Kaggle US dataset contains 825 records across 107 games.
  Its loader standardizes headers; it is not connected to the Australian
  reconstruction or model.

## Files and code flow

```text
src/
├── load_zbw.py
├── load_kaggle.py
├── cleaner.py
├── build_dataset.py
├── features.py
└── analysis.py

data/raw/
├── zbw/deal-data.txt
├── zbw/readme.rs.txt
└── kaggle/dond_game_data.csv

tests/
├── conftest.py
├── unit/
│   ├── test_load_zbw.py
│   ├── test_cleaner.py
│   ├── test_build_dataset.py
│   ├── test_features.py
│   └── test_analysis.py
└── integration/test_pipeline.py

pytest.ini
requirements.txt
```

```text
load_zbw()
  → clean()
  → build_dataset()
  → build_features()
  → run_analysis()
```

| File | Responsibility |
|---|---|
| [load_zbw.py](src/load_zbw.py) | Read the 20-field source, replace missing markers, cast rounds and series IDs, validate identifiers, and add a date. |
| [load_kaggle.py](src/load_kaggle.py) | Load the US CSV and normalize column names. |
| [cleaner.py](src/cleaner.py) | Check mixed-series metadata before filtering; keep Series 2.00, 3.00, 3.10; remove whole special-show games. |
| [build_dataset.py](src/build_dataset.py) | Reconstruct boards by series, calculate EV and offer/EV, and record failed games separately. |
| [features.py](src/features.py) | Build board and lag features, validate offer ratios, and select active decision offers. |
| [analysis.py](src/analysis.py) | Fit the pooled and per-series logit models and report marginal effects. |

### Reconstruction

Each game starts with a 26-prize board selected by series. Series 2.11 has
two $200,000 prizes; Series 2.20 uses a special board with a $2 million maximum.
The other supported series use the standard main board.

Opened prizes are removed in round order. Each round receives:

| Column | Meaning |
|---|---|
| `remaining_board` | Remaining prizes after that round's removals |
| `n_remaining` | Number of prizes left |
| `board_ev` | Mean remaining prize; missing for an empty board |
| `offer_ev_ratio` | Banker offer divided by current board EV |

A prize mismatch excludes the entire game and records its show, series,
round, and offending prize in the error report.

### Offer-level features

The feature builder accepts board lists or their CSV string representation.
It adds 11 columns:

- `board_list`: parsed remaining prizes.
- `log_board_ev`, `board_min`, `board_max`, `prob_above_ev`, and
  `board_skew`: board distribution features.
- `board_ev_prev` and `ev_change_prev`: previous EV and its change.
- `normalized_luck`: EV change divided by previous EV.
- `luck_undefined`: true when normalized luck is missing.
- `offers_declined`: earlier No Deals, excluding the current decision.

Lags are computed before filtering to offers, so non-offer rounds remain
available as prior game states. Luck is undefined for a missing or zero prior
EV and whenever the preceding recorded round is not exactly one round earlier.

The output retains the accepted Deal, removes all later rounds, and excludes
empty terminal boards. First offers remain in the feature output; the model
then excludes rows with undefined luck.

### Baseline model

```text
decision ~ normalized_luck
         + offer_ev_ratio
         + log_board_ev
         + n_remaining
         + round
         + C(series_id)
```

- `decision=1` means Deal; `0` means No Deal.
- Standard errors are clustered by game to account for repeated observations.
- `offers_declined` is excluded from the formula because it equals
  `round - 1` in this sample.
- The report includes sample counts, Deal rate, predictor distributions,
  the luck coefficient, and its marginal effect at predictor means.
- Absolute luck–offer-ratio correlation above 0.5 produces a collinearity note.
- Separate series fits use clustered errors and require at least 50 rows.
- Separation, rank deficiency, nonconvergence, and nonfinite estimates prevent
  reporting an unreliable fit. Directional sign warnings are diagnostic,
  not assertions that the expected hypothesis must hold.

## Validation and bug fixes

Production validation uses explicit exceptions, so it remains active under
`python -O`. Tests cover:

- Exactly 20 fields per raw record, preventing silent padding of short rows.
- Missing IDs, invalid rounds/series, mixed-series games, and duplicate rounds.
- Empty and all-failed reconstruction outputs with preserved column names.
- Malformed boards, invalid decisions, negative/nonfinite values, and
  disagreement between board lists, EV, and remaining-prize counts.
- Finite supplied offer/EV ratios checked against their inputs with a
  `1e-6` absolute tolerance.
- Undefined luck across round gaps and preservation of missing luck.
- Whole-show contamination, post-Deal removal, and terminal-board exclusion.
- Replacement of stale output CSVs, including when results are empty.
- Model sample validation, clustered fitting, and convergence safeguards.

A physically complete record containing `-999` remains a valid missing-value
record. Field-count validation cannot infer an unrecorded prize from that
marker. Likewise, round-gap handling marks luck undefined; it does not
reconstruct an omitted round.

## Setup and execution

Run commands from this project directory. Dependencies are pandas, NumPy,
SciPy, statsmodels, and pytest, with minimum versions in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Inspect either dataset:

```bash
python src/load_zbw.py
python src/load_kaggle.py
```

Reconstruct the **full raw ZBW dataset** and write its two CSV outputs:

```bash
python src/build_dataset.py
```

The command clears old outputs before processing and writes both files after
reconstruction, including headers for empty results:

- `data/processed/zbw_reconstructed.csv`
- `data/processed/zbw_board_mismatches.csv`

Input-validation failure leaves the cleared files empty. Generated CSVs,
virtual environments, and caches are ignored by Git.

Run the complete **cleaned** analysis in memory:

```bash
PYTHONPATH=src python - <<'PY'
from load_zbw import load_zbw
from cleaner import clean
from build_dataset import build_dataset
from features import build_features
from analysis import run_analysis

raw = load_zbw()
cleaned = clean(raw)
reconstructed, mismatches = build_dataset(cleaned)
offers = build_features(reconstructed)
result = run_analysis(offers)
PY
```

The cleaned chain prints model results. It does not automatically save a
feature CSV or fitted model. There is no combined pipeline CLI; the functions
are connected by the example above and the integration tests.

## Tests

There are **87 tests: 83 unit tests and four real-data integration tests**.
Shared fixtures provide small synthetic games and model samples. The suite
checks normal outputs, malformed inputs, empty results, CSV reruns, and
optimized Python. The integration tests verify the stage counts above and a
converged real-data model.

Run all tests:

```bash
python -m pytest tests -q --strict-markers
```

Run unit tests, integration tests, or the optimized-Python regression test:

```bash
python -m pytest tests/unit -q
python -m pytest -m integration -v
python -m pytest tests/unit/test_features.py -k optimized -v
```

`pytest.ini` defines local discovery and the `integration`/`slow` markers.
A deselected test is outside the chosen subset, not a failure.
