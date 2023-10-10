"""Kedro Project settings."""
import logging

from kedro.config import TemplatedConfigLoader

from application.spi.kedro.hooks import ProjectHooks

HOOKS = (ProjectHooks(),)

CONFIG_LOADER_CLASS = TemplatedConfigLoader
CONFIG_LOADER_ARGS = {"globals_pattern": "*globals.yml"}

logger = logging.getLogger(__name__)
