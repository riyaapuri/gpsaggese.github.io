from pathlib import Path
import pandas as pd

from load_zbw import load_zbw


# ============================================================
# PRIZE BOARDS
# ============================================================

# Standard Australian Deal or No Deal board.
# Used for Series 2.00, 2.10, 3.00 and 3.10.
STANDARD_BOARD = [
    0.5,
    1,
    2,
    5,
    10,
    25,
    50,
    75,
    100,
    150,
    250,
    500,
    750,
    1000,
    1500,
    2000,
    3000,
    5000,
    7500,
    10000,
    15000,
    25000,
    50000,
    75000,
    100000,
    200000,
]


# Series 2.11:
# $1,500 was replaced by a second $200,000 prize.
SERIES_2_11_BOARD = [
    0.5,
    1,
    2,
    5,
    10,
    25,
    50,
    75,
    100,
    150,
    250,
    500,
    750,
    1000,
    2000,
    3000,
    5000,
    7500,
    10000,
    15000,
    25000,
    50000,
    75000,
    100000,
    200000,
    200000,
]


# Series 2.20:
# Prime-time special board with prizes up to $2 million.
SERIES_2_20_BOARD = [
    0.5,
    1,
    2,
    5,
    10,
    25,
    50,
    75,
    100,
    200,
    300,
    500,
    750,
    1000,
    2500,
    5000,
    7500,
    10000,
    25000,
    50000,
    75000,
    100000,
    250000,
    500000,
    1000000,
    2000000,
]


# Match each series_id to its starting board.
BOARDS = {
    2.00: STANDARD_BOARD,
    2.10: STANDARD_BOARD,
    2.11: SERIES_2_11_BOARD,
    2.20: SERIES_2_20_BOARD,
    3.00: STANDARD_BOARD,
    3.10: STANDARD_BOARD,
}


CASE_COLUMNS = [
    "case_1",
    "case_2",
    "case_3",
    "case_4",
    "case_5",
    "case_6",
]


# ============================================================
# RECONSTRUCT ONE SHOW
# ============================================================

def reconstruct_show(show_df, starting_board):
    """
    Reconstruct the remaining prize board after each round
    for one contestant/show.
    """

    show_df = show_df.sort_values("round").copy()

    # Every contestant starts with a fresh copy of the board.
    remaining = starting_board.copy()

    remaining_boards = []
    n_remaining_list = []
    board_ev_list = []

    for _, row in show_df.iterrows():

        # Remove every prize opened during the current round.
        for col in CASE_COLUMNS:

            value = row[col]

            if pd.notna(value):

                value = float(value)

                # If an opened value is no longer on our assumed board,
                # this show cannot be reconstructed using that board.
                if value not in remaining:
                    raise ValueError(
                        f"BOARD_MISMATCH | "
                        f"show={row['show_id']} | "
                        f"series={row['series_id']} | "
                        f"round={row['round']} | "
                        f"value={value}"
                    )

                remaining.remove(value)

        # The bank offer is made after the cases for the round
        # have been opened, so this is the board relevant
        # to the Deal / No Deal decision.
        current_board = remaining.copy()

        remaining_boards.append(current_board)

        n_remaining_list.append(
            len(current_board)
        )

        if len(current_board) > 0:
            board_ev = (
                sum(current_board)
                / len(current_board)
            )
        else:
            board_ev = pd.NA

        board_ev_list.append(board_ev)

    # Add reconstructed variables.
    show_df["remaining_board"] = remaining_boards

    show_df["n_remaining"] = n_remaining_list

    show_df["board_ev"] = board_ev_list

    # Banker offer relative to the expected value
    # of the remaining board.
    show_df["offer_ev_ratio"] = (
        show_df["bank_offer"]
        / show_df["board_ev"]
    )

    return show_df


# ============================================================
# BUILD FULL DATASET
# ============================================================

def build_dataset(df):
    """
    Attempt board reconstruction for every show.

    Valid shows are returned in the reconstructed dataset.

    Shows whose observed case values do not match the assumed
    starting board are recorded separately as mismatches.
    """

    reconstructed_games = []
    mismatches = []

    for show_id, show_df in df.groupby("show_id"):

        series_id = float(
            show_df["series_id"].iloc[0]
        )

        # Check that we know which board belongs to this series.
        if series_id not in BOARDS:

            mismatches.append({
                "show_id": show_id,
                "series_id": series_id,
                "error": "No starting board defined",
            })

            continue

        starting_board = BOARDS[series_id]

        try:

            game = reconstruct_show(
                show_df,
                starting_board,
            )

            reconstructed_games.append(game)

        except ValueError as error:

            mismatches.append({
                "show_id": show_id,
                "series_id": series_id,
                "error": str(error),
            })

    # Combine all successfully reconstructed shows.
    if reconstructed_games:

        reconstructed_df = pd.concat(
            reconstructed_games,
            ignore_index=True,
        )

    else:

        reconstructed_df = pd.DataFrame()

    mismatch_df = pd.DataFrame(mismatches)

    return reconstructed_df, mismatch_df


# ============================================================
# RUN SCRIPT
# ============================================================

if __name__ == "__main__":

    # Load raw ZBW dataset.
    df = load_zbw()

    print("\n--------------------------------")
    print("ZBW BOARD RECONSTRUCTION")
    print("--------------------------------")

    print(f"\nRaw rows: {len(df)}")
    print(
        f"Raw shows: "
        f"{df['show_id'].nunique()}"
    )

    # Reconstruct all possible shows.
    reconstructed_df, mismatch_df = (
        build_dataset(df)
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    successful_shows = (
        reconstructed_df["show_id"].nunique()
        if not reconstructed_df.empty
        else 0
    )

    failed_shows = len(mismatch_df)

    total_shows = df["show_id"].nunique()

    print("\nReconstruction summary:")
    print(
        f"Successful shows: "
        f"{successful_shows} / {total_shows}"
    )
    print(
        f"Board mismatches: "
        f"{failed_shows}"
    )

    # --------------------------------------------------------
    # Display mismatches
    # --------------------------------------------------------

    if not mismatch_df.empty:

        print("\nShows with board mismatches:")

        print(
            mismatch_df.to_string(
                index=False
            )
        )

    else:

        print(
            "\nNo board mismatches found."
        )

    # --------------------------------------------------------
    # Save reconstructed data
    # --------------------------------------------------------

    output_dir = Path(
        "data/processed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not reconstructed_df.empty:

        save_df = (
            reconstructed_df.copy()
        )

        # Lists need to be converted to strings
        # before writing to CSV.
        save_df["remaining_board"] = (
            save_df["remaining_board"]
            .astype(str)
        )

        reconstructed_path = (
            output_dir
            / "zbw_reconstructed.csv"
        )

        save_df.to_csv(
            reconstructed_path,
            index=False,
        )

        print(
            f"\nReconstructed dataset saved to:"
            f"\n{reconstructed_path}"
        )

    # --------------------------------------------------------
    # Save mismatches separately
    # --------------------------------------------------------

    if not mismatch_df.empty:

        mismatch_path = (
            output_dir
            / "zbw_board_mismatches.csv"
        )

        mismatch_df.to_csv(
            mismatch_path,
            index=False,
        )

        print(
            f"\nBoard mismatch report saved to:"
            f"\n{mismatch_path}"
        )

    # --------------------------------------------------------
    # Preview new variables
    # --------------------------------------------------------

    if not reconstructed_df.empty:

        print("\nPreview:")

        preview_columns = [
            "show_id",
            "series_id",
            "round",
            "bank_offer",
            "decision",
            "n_remaining",
            "board_ev",
            "offer_ev_ratio",
        ]

        print(
            reconstructed_df[
                preview_columns
            ].head(15)
        )