from pathlib import Path
import pandas as pd

ZBW_COLUMNS = [
    "year", "month", "day", "show_id", "series_id", "round",
    "gender", "special_show", "superamount", "contestant_guess",
    "contestant_precision", "bank_offer", "audience_suggestion",
    "decision", "case_1", "case_2", "case_3", "case_4", "case_5", "case_6",
]

def load_zbw(path="data/raw/zbw/deal-data.txt"):
    """Load the ZBW/de Roos & Sarafidis round-level dataset."""
    path = Path(path)
    df = pd.read_csv(path, sep=r"\s+", header=None, names=ZBW_COLUMNS)
    df = df.replace(-999, pd.NA)

    # Useful date field while retaining original year/month/day columns.
    df["date"] = pd.to_datetime(
        df[["year", "month", "day"]].rename(
            columns={"year": "year", "month": "month", "day": "day"}
        ),
        errors="coerce",
    )
    return df

if __name__ == "__main__":
    df = load_zbw()
    print(df.head())
    print("\nShape:", df.shape)
    print("Shows:", df["show_id"].nunique())
    print("\nMissing values:")
    print(df.isna().sum())
