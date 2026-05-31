import pandas as pd


# ============================================================
# 📊 DATA ANALYSIS FUNCTION
# ============================================================

def analyze_data(df):

    result = {}

    # ------------------------------------------------
    # BASIC INFO
    # ------------------------------------------------
    result["shape"] = df.shape
    result["columns"] = df.columns.tolist()

    # ------------------------------------------------
    # MISSING VALUES
    # ------------------------------------------------
    result["missing_values"] = df.isnull().sum().to_dict()

    # ------------------------------------------------
    # DUPLICATES
    # ------------------------------------------------
    result["duplicates"] = int(df.duplicated().sum())

    # ------------------------------------------------
    # NUMERIC COLUMNS
    # ------------------------------------------------
    numeric_df = df.select_dtypes(include=["number"])

    if not numeric_df.empty:

        result["statistics"] = numeric_df.describe().to_dict()

        result["highest_values"] = {
            col: float(numeric_df[col].max())
            for col in numeric_df.columns
        }

        result["lowest_values"] = {
            col: float(numeric_df[col].min())
            for col in numeric_df.columns
        }

        result["average_values"] = {
            col: float(round(numeric_df[col].mean(), 2))
            for col in numeric_df.columns
        }

    else:
        result["statistics"] = "No numeric data found"

    return result