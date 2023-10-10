"""Etl runtime checks"""
import logging
from typing import List

from pandas import DataFrame

logger = logging.getLogger(__name__)


def verify_primary_key_or_fail(input_df: DataFrame, key_column_list: List[str]) -> None:
    """
    Raise and log and error if the input table primary key is violated
    """
    if input_df.shape[0] != input_df[key_column_list].drop_duplicates().shape[0]:
        sample = (
            input_df.groupby(key_column_list, as_index=False)
            .agg(line_count=(key_column_list[0], "count"))
            .sort_values("line_count", ascending=False)
        )
        exception_str = "Failed to validate dataset cardinality"
        logger.error(exception_str, extra={"columns": key_column_list, "sample": sample.head(5)})
        raise Exception(exception_str)


def verify_not_empty_or_fail(input_df: DataFrame) -> None:
    """
    Raise and log and error if the input dataset is empty
    """
    if input_df.empty:
        exception_str = "Dataset is empty"
        logger.error(exception_str)
        raise Exception(exception_str)
