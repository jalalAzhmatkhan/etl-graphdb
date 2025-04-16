from typing import List

import numpy as np
import pandas as pd

def batch_dataframe(
    df: pd.DataFrame,
    batch_size: int = 1000
)->List[pd.DataFrame]:
    """
    Batches a Pandas DataFrame into smaller DataFrames of a specified size.

    Args:
        :param df: The Pandas DataFrame to batch.
        :param batch_size: The desired number of rows in each batch.

    Returns:
        A list of Pandas DataFrames, each containing a batch of rows.
    """
    batches = []
    for i in np.array_split(df.index, np.ceil(len(df) / batch_size)):
        batches.append(df.loc[i])  # or df.iloc[i] depending on your index type
    return batches


def create_concatenated_string_list_vectorized(
    df_input: pd.DataFrame,
    concat_symbol: str = "|"
)->List[str]:
    """
    Create a concatenated string list from a DataFrame.

    Args:
        :param df_input: The DataFrame to process.
        :param concat_symbol: The symbol to use for concatenation.

    Returns:
        A list of concatenated strings.
    """
    return df_input.apply(
        lambda row: concat_symbol.join(row.values.astype(str)),
        axis=1
    ).tolist()
