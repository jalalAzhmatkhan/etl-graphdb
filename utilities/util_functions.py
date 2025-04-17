import re
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
    df_filled = df_input.fillna("")
    return df_filled.apply(
        lambda row: concat_symbol.join(row.values.astype(str)),
        axis=1
    ).tolist()

def uniforms_nomenclature_naming(
    nomenclature_name_input: str
)->str:
    """
    Uniforms the nomenclature naming
    :param nomenclature_name_input:
    :return:
    """
    match = re.match(r"([A-Z]+)-([A-Z]\d)-([A-Z]+)(\d+)-([A-Z])(\d+)", nomenclature_name_input)

    if match:
        part_1 = match.group(1)  # PLGS
        part_2 = match.group(2)  # C1
        part_3 = match.group(3)  # ACB
        number_1 = int(match.group(4))  # 11 or 4
        part_5 = match.group(5)  # Z
        number_2 = int(match.group(6))  # 11 or 1

        # Format the numbers to 2 digits
        formatted_number_1 = f"{number_1:02}"
        formatted_number_2 = f"{number_2:02}"

        return f"{part_1}-{part_2}-{part_3}-{formatted_number_1}-{formatted_number_2}"

    return nomenclature_name_input
