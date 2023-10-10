import pandas as pd
from pandas.testing import assert_frame_equal

from application.etl.intermediate import intermediate_test


def test_intermediate_test() -> None:
    input_df = pd.DataFrame(
        columns=["test_column_a", "test_column_b"],
        data=[
            ("abc", "def"),
            ("123", "456"),
        ],
    )

    expected = pd.DataFrame(
        columns=["test_column_a", "test_column_b"],
        data=[
            ("abc", "def"),
            ("123", "456"),
        ],
    )

    assert_frame_equal(
        intermediate_test(input_df),
        expected,
        check_like=True,
    )
