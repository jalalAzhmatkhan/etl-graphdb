import os

import pandas as pd

from settings import settings

def searching_in_acmv(query: str):
    df_acmv = pd.read_csv(os.path.join(settings.OUTPUT_DIR, "plg_acmv_relationship_transformed.csv"))
    search_columns = ["1st Layer", "2nd Layer", "3rd Layer"]
    found_in_col = ""
    mask = False
    for col in search_columns:
        mask = mask | df_acmv[col].str.contains(recreated_query, na=False)
        if True in df_acmv[col].str.contains(recreated_query, na=False).tolist():
            found_in_col = col
    result_df = df_acmv[mask].copy()
    result_df["found_in_col"] = found_in_col
    print(result_df)

if __name__ == "__main__":
    recreated_query = "C1-AHU-12-08"
    searching_in_acmv(recreated_query)
