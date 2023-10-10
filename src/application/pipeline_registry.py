"""Pipeline nodes manifest (`kedro viz` to visualize dependencies as a graph)."""
from typing import Dict

from kedro.pipeline import Pipeline, node

from application.etl.intermediate import intermediate_test


def register_pipelines() -> Dict[str, Pipeline]:
    return {
        "main": Pipeline(
            [
                node(
                    intermediate_test,
                    inputs="raw_test",
                    outputs="intermediate_test",
                    name="intermediate_test_node",
                )
            ]
        )
    }
