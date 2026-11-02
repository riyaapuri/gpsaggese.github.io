
# Causal Analysis of Deal or No Deal

## Project Overview

This project investigates decision-making under risk using data from the television game show *Deal or No Deal*. We aim to understand how contestants make decisions under uncertainty, how previous outcomes influence their choices, and whether their behavior aligns with rational decision-making strategies.

Our approach focuses on reconstructing game states, analyzing banker offers, and evaluating contestant decisions using statistical and causal inference methods.

## Dataset Exploration

We are evaluating multiple publicly available datasets to identify the sources with the highest resolution and most complete game histories.

### 1. ZBW — Australian Deal or No Deal

**Primary dataset candidate**

Associated study: de Roos and Sarafidis (2010), *Decision Making Under Risk in Deal or No Deal*.

- 4,664 round-level observations across 424 shows.
- Banker offers and contestant Deal/No Deal decisions.
- Case elimination values recorded by round.
- Contestant characteristics and special-game indicators.
- Remaining prize boards and expected values can be reconstructed.

**Current reconstruction results:**
- Successfully reconstructed 422 out of 424 shows (99.53%).
- Calculated remaining board size, expected value, and offer-to-EV ratio.
- Identified two board mismatches (shows 336 and 1003) for further investigation.
- Preserved mismatch details separately for validation.

### 2. Kaggle — US Deal or No Deal

Secondary dataset containing approximately 107 games and 825 observations. Currently being evaluated for completeness, round-level coverage, and potential comparative analysis.

### 3. Additional Academic Datasets

Other published research datasets and replication packages are being reviewed to compare game coverage, available variables, and data quality.

### Dataset Selection Criteria

Datasets are compared based on:
- Number of games and observations
- Round-level banker offers and decisions
- Case eliminations and remaining board information
- Historical game states
- Final outcomes and payouts
- Data completeness and reliability

## Project Structure

    causal-deal-or-no-deal/
    ├── data/
    │   ├── raw/
    │   │   ├── zbw/
    │   │   └── kaggle/
    │   └── processed/
    ├── notebooks/
    │   └── 01_data_exploration.ipynb
    ├── src/
    │   ├── load_zbw.py
    │   ├── load_kaggle.py
    │   └── build_dataset.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## Data Processing Pipeline

### 1. Data Loading

- `load_zbw.py`: Loads and inspects the Australian dataset, including missing values, series information, and contestant records.
- `load_kaggle.py`: Loads the US dataset for exploratory analysis and comparison.

### 2. Board Reconstruction

`build_dataset.py` reconstructs the remaining prize board for each show by sequentially removing the case values opened in each round.

The following variables are generated:

| Variable | Description |
|----------|-------------|
| `remaining_board` | Prize values remaining after each round |
| `n_remaining` | Number of remaining prizes |
| `board_ev` | Expected value of the remaining prize board |
| `offer_ev_ratio` | Banker offer divided by board expected value |

The script validates observed eliminations against the expected prize boards and records any mismatches separately.

### 3. Generated Outputs

- `data/processed/zbw_reconstructed.csv` — Reconstructed game states and derived variables for 422 shows.
- `data/processed/zbw_board_mismatches.csv` — Records of shows that could not be reconstructed using the current board definitions.

## Setup and Execution

### 1. Create a virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Run dataset exploration

    python src/load_zbw.py
    python src/load_kaggle.py

### 4. Reconstruct game states

    python src/build_dataset.py

## Implementation Plan

### Phase 1: Dataset Discovery and Evaluation
- Identify and compare available academic and public datasets.
- Evaluate game coverage, granularity, and missing information.
- Select the highest-resolution dataset for primary analysis.

### Phase 2: Data Preparation and Validation
- Reconstruct remaining prize boards and expected values.
- Validate game histories and investigate reconstruction mismatches.
- Create a consistent round-level dataset for modeling.

### Phase 3: Exploratory Analysis
- Analyze banker offers relative to expected value.
- Examine Deal/No Deal decisions across rounds.
- Investigate the effects of previous outcomes and game progression.

### Phase 4: Decision Modeling and Causal Analysis
- Develop benchmark decision-making strategies.
- Model contestant risk preferences.
- Investigate the influence of previous outcomes while accounting for the current game state.
- Evaluate banker-offer predictability and contestant decision patterns.

### Phase 5: Evaluation and Reporting
- Compare observed decisions with benchmark strategies.
- Assess model performance and robustness.
- Summarize findings, limitations, and future research directions.


## Team

**MSML610 — Fall 2026, Group 28**

- Stuti Patel
- Riya Puri
