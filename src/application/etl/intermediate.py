from typing import Callable

import numpy as np
import pandas as pd
from pandera import Field, SchemaModel, check_output, typing

from application.etl.runtime_checks import (
    verify_not_empty_or_fail,
    verify_primary_key_or_fail,
)


def _remove_leading_zeros(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lstrip("0")


def _remove_trailing_float_zero(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True)


def _remove_whitespace(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\s", "", regex=True)


def standardize_column_names(f: Callable) -> Callable:  # type: ignore [type-arg]
    def clean_null_cols(df: pd.DataFrame) -> pd.DataFrame:
        return df.replace(r"(\s*)(NULL)(\s*)", np.nan, regex=True)

    def lowercase_column_names(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.lower()
        return df

    def underscore_column_names(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.replace(" ", "_")
        return df

    def wrapper(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:  # type: ignore [no-untyped-def]
        return f(
            df.pipe(lowercase_column_names).pipe(underscore_column_names).pipe(clean_null_cols),
            *args,
            **kwargs,
        )

    return wrapper


class Test(SchemaModel):  # type: ignore[misc]
    test_column_a: typing.Series[str] = Field(nullable=True)
    test_column_b: typing.Series[str] = Field(nullable=True)

    class Config:
        strict = True


@check_output(Test)  # type: ignore[misc]
@standardize_column_names
def intermediate_test(df: pd.DataFrame) -> pd.DataFrame:
    verify_primary_key_or_fail(df, ["test_column_a"])
    verify_not_empty_or_fail(df)
    return df
