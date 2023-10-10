"""Command line tools for manipulating a Kedro project.
Intended to be invoked via `kedro`."""
import logging
import os
from itertools import chain
from pathlib import Path
from typing import Iterable, Tuple

import click  # type: ignore
from kedro.framework.cli.utils import (
    KedroCliError,
    _config_file_callback,
    _reformat_load_versions,
    _split_params,
    env_option,
    split_string,
)
from kedro.framework.session import KedroSession
from kedro.io import DataSetError
from kedro.utils import load_obj
from mdc import MDC  # type: ignore

from application.config import Config
from application.spi.azure import get_secret

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

FROM_INPUTS_HELP = """A list of dataset names which should be used as a starting point."""
TO_OUTPUTS_HELP = """A list of dataset names which should be used as an end point."""
FROM_NODES_HELP = """A list of node names which should be used as a starting point."""
TO_NODES_HELP = """A list of node names which should be used as an end point."""
NODE_ARG_HELP = """Run only nodes with specified names."""
RUNNER_ARG_HELP = """Specify a runner that you want to run the pipeline with.
Available runners: `SequentialRunner`, `ParallelRunner` and `ThreadRunner`.
This option cannot be used together with --parallel."""
PARALLEL_ARG_HELP = """Run the pipeline using the `ParallelRunner`.
If not specified, use the `SequentialRunner`. This flag cannot be used together
with --runner."""
ASYNC_ARG_HELP = """Load and save node inputs and outputs asynchronously
with threads. If not specified, load and save datasets synchronously."""
TAG_ARG_HELP = """Construct the pipeline using only nodes which have this tag
attached. Option can be used multiple times, what results in a
pipeline constructed from nodes having any of those tags."""
LOAD_VERSION_HELP = """Specify a particular dataset version (timestamp) for loading."""
CONFIG_FILE_HELP = """Specify a YAML configuration file to load the run
command arguments from. If command line arguments are provided, they will
override the loaded ones."""
PIPELINE_ARG_HELP = """Name of the modular pipeline to run.
If not set, the project pipeline is run by default."""
PARAMS_ARG_HELP = """Specify extra parameters that you want to pass
to the context initializer. Items must be separated by comma, keys - by colon,
example: param1:value1,param2:value2. Each parameter is split by the first comma,
so parameter values are allowed to contain colons, parameter keys are not."""


def _get_values_as_tuple(values: Iterable[str]) -> Tuple[str, ...]:
    return tuple(chain.from_iterable(value.split(",") for value in values))


@click.group(context_settings=CONTEXT_SETTINGS, name=__file__)  # type: ignore
def cli() -> None:
    """Command line tools for manipulating a Kedro project."""


@cli.command()  # type: ignore
@click.option(  # type: ignore
    "--from-inputs", type=str, default="", help=FROM_INPUTS_HELP, callback=split_string
)
@click.option(  # type: ignore
    "--to-outputs", type=str, default="", help=TO_OUTPUTS_HELP, callback=split_string
)
@click.option(  # type: ignore
    "--from-nodes", type=str, default="", help=FROM_NODES_HELP, callback=split_string
)
@click.option(  # type: ignore
    "--to-nodes", type=str, default="", help=TO_NODES_HELP, callback=split_string
)
@click.option(  # type: ignore
    "--node", "-n", "node_names", type=str, multiple=True, help=NODE_ARG_HELP
)
@click.option(  # type: ignore
    "--runner", "-r", type=str, default=None, multiple=False, help=RUNNER_ARG_HELP
)
@click.option(  # type: ignore
    "--parallel", "-p", is_flag=True, multiple=False, help=PARALLEL_ARG_HELP
)
@click.option(  # type: ignore
    "--async", "is_async", is_flag=True, multiple=False, help=ASYNC_ARG_HELP
)
@env_option  # type: ignore [misc]
@click.option("--tag", "-t", type=str, multiple=True, help=TAG_ARG_HELP)  # type: ignore
@click.option(  # type: ignore
    "--load-version",
    "-lv",
    type=str,
    multiple=True,
    help=LOAD_VERSION_HELP,
    callback=_reformat_load_versions,
)
@click.option("--pipeline", type=str, default=None, help=PIPELINE_ARG_HELP)  # type: ignore
@click.option(  # type: ignore
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help=CONFIG_FILE_HELP,
    callback=_config_file_callback,
)
@click.option(  # type: ignore
    "--params", type=str, default="", help=PARAMS_ARG_HELP, callback=_split_params
)
def run(  # type: ignore # noqa: C901
    tag,
    env,
    parallel,
    runner,
    is_async,
    node_names,
    to_nodes,
    from_nodes,
    from_inputs,
    to_outputs,
    load_version,
    pipeline,
    config,
    params,
) -> None:  # type: ignore # pragma: no cover
    """Run the pipeline."""
    if parallel and runner:
        raise KedroCliError(
            "Both --parallel and --runner options cannot be used together. "
            "Please use either --parallel or --runner."
        )
    runner = runner or "SequentialRunner"
    if parallel:
        runner = "ParallelRunner"
    runner_class = load_obj(runner, "kedro.runner")

    tag = _get_values_as_tuple(tag) if tag else tag
    node_names = _get_values_as_tuple(node_names) if node_names else node_names

    package_name = str(Path(__file__).resolve().parent.name)

    # used for SnowFlakeConfig data class
    os.environ["KEDRO_ENV"] = env

    if env != "test":
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = get_secret(
            "APP-azure-storage-connection-string-7851"
        )

    if env not in ["base", "test"]:
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = get_secret(
            "APP-applicationinsights-connection-string-7637"
        )

    with KedroSession.create(package_name, env=env, extra_params=params) as session:
        with MDC(service="application", env=env, git_head=Config.git_head()):
            try:
                session.run(
                    tags=tag,
                    runner=runner_class(is_async=is_async),
                    node_names=node_names,
                    from_nodes=from_nodes,
                    to_nodes=to_nodes,
                    from_inputs=from_inputs,
                    to_outputs=to_outputs,
                    load_versions=load_version,
                    pipeline_name=pipeline,
                )
            except DataSetError as e:

                def cleanup(line: str) -> str:
                    if line.startswith("[SQL:"):
                        return line[:1000] + "..."
                    elif line.startswith("[parameters:"):
                        return "[parameters: <REDACTED>]"
                    else:
                        return line

                logging.getLogger(__name__).error("\n".join(cleanup(l) for l in str(e).split("\n")))
                exit(1)
            except Exception as e:
                logging.getLogger(__name__).exception(e)
                exit(1)
