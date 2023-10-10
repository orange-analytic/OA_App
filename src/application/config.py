"""Global Propel configuration values."""

import os
from dataclasses import dataclass

GLOBAL_SEED_VALUE = 1234


@dataclass
class SnowflakeConfig:  # pragma: no cover
    database: str
    schema: str
    role: str
    warehouse: str
    account: str = "change me"
    protocol: str = "https"
    authenticator: str = "oauth"


class Config:  # pragma: no cover
    project_path = os.path.join(os.path.dirname(__file__), "..", "..")
    data_path = os.path.join(project_path, "data")

    @classmethod
    def git_head(cls) -> str:
        file_path = os.path.join(cls.project_path, "git_head.txt")
        if not os.path.exists(file_path):
            return "local-head"
        with open(file_path) as f:
            git_head = "".join([line.replace("\n", "") for line in f.readlines()])
            return git_head


PRODUCT_LINE_CODE = {"key": "value"}

MODEL_CONFIG_TIME_SERIES = {
    "problem_type": "time_series",
    "filter_on_mature_market": False,
    "filter_on_product_line": "key",
    "test_year_lags": [-9, -6, -3],
    "max_targets": 3,
    "max_feature_lags": 3,
}

MODEL_CONFIG_REGRESSION = {
    "problem_type": "regression",
    "filter_on_mature_market": True,
    "filter_on_product_line": "key",
    "train_split": 0.7,
    "cv_folds": 10,
    "max_targets": 3,
}
