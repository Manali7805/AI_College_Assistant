import pandas as pd

def analyze_results(df):

    # Clean column names
    df.columns = df.columns.str.strip()

    # ------------------ FIX SGPA COLUMN ------------------
    sgpa_col = None
    for col in df.columns:
        if "sgpa" in col.lower():
            sgpa_col = col
            break

    if sgpa_col:
        df.rename(columns={sgpa_col: "SGPA"}, inplace=True)

        df["SGPA"] = (
            df["SGPA"]
            .astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
            .str.extract(r'(\d+(?:\.\d+)?)', expand=False)
        )

        df["SGPA"] = pd.to_numeric(df["SGPA"], errors="coerce")

    # ------------------ REMOVE EMPTY ROWS ------------------
    df = df.dropna(how="all")

    # ------------------ SUBJECT DETECTION ------------------
    ignore_cols = ["Name", "SGPA", "Total", "Average", "Status", "Grade"]

    subject_cols = [col for col in df.columns if col not in ignore_cols]

    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------ CALCULATIONS ------------------
    if subject_cols:
        df["Total"] = df[subject_cols].sum(axis=1)
        df["Average"] = df[subject_cols].mean(axis=1)

        df["Status"] = df[subject_cols].apply(
            lambda x: "Pass" if all(x.fillna(0) >= 40) else "Fail",
            axis=1
        )
    else:
        df["Total"] = 0
        df["Average"] = 0
        df["Status"] = "N/A"

    # ------------------ GRADING ------------------
    def grade(avg):
        if avg >= 90: return "A+"
        elif avg >= 75: return "A"
        elif avg >= 60: return "B"
        elif avg >= 50: return "C"
        else: return "F"

    df["Grade"] = df["Average"].apply(grade)

    return df