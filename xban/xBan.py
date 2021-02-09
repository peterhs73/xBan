#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
import logging
from xban.gui import main_app
from xban.io import process_yaml


cli_logger = logging.getLogger("xban-cli")

# MODUEL PATH
BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")


@click.group()
@click.option("-d/ ", "--debug/--no-debug", default=False, help="Toggle debug mode")
def cli(debug):
    """Command-line interface

    FILE should be the path or a valid yaml file
    """

    root_logger = logging.getLogger()
    if debug:
        click.echo("Debug mode on")
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


@click.command()
@click.argument("filepath", type=click.Path(exists=True, resolve_path=True))
def render(filepath):
    """Render existing files

    FILEPATH should be the path or a valid yaml file
    """

    file_config = process_yaml(filepath)

    if file_config:
        main_app(BASE_PATH, filepath, file_config)


@click.command()
@click.argument("filepath", type=click.Path(resolve_path=True))
def create(filepath):
    """Create new file

    FILEPATH should a valid filepath with correct extension
    """
    file_dir, filename = os.path.split(filepath)
    if os.path.isfile(filepath):
        cli_logger.error(
            f"{filepath} already exist, use command: xban render {filepath}"
        )
    elif not file_dir:
        cli_logger.error(f"directory {file_dir} does not exist")
    else:
        with open(filepath, "w+"):
            pass
        file_config = process_yaml(filepath)
        main_app(BASE_PATH, filepath, file_config)


cli.add_command(render)
cli.add_command(create)
