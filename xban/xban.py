#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
import logging
from xban.mainwindow import main_app
from xban.io import process_yaml


cli_logger = logging.getLogger("xban-cli")

# MODUEL PATH
BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")


"""The command line interface, the handler is called from setup.py
"""

@click.command()
@click.option(
    "-d/ ", "--debug", is_flag=True, default=False, help="Toggle debug mode"
)
@click.argument("filepath", type=click.Path(resolve_path=True))
def cli(debug, filepath):

    """FILEPATH should be a valid filepath with correct extension

    xBan renders if the input file is a valid format,
    or asks to create a new file if does not exist
    """

    root_logger = logging.getLogger()
    if debug:
        click.echo("Debug mode on")
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    # check filepath

    file_dir, filename = os.path.split(filepath)
    if os.path.isfile(filepath):
        file_config = process_yaml(filepath)

        if file_config:
            main_app(BASE_PATH, filepath, file_config)
        else:
            cli_logger.error(f'{file_dir} is not a valid ymal file')

    elif not file_dir:
        cli_logger.error(f"directory {file_dir} does not exist")
    
    # create new file if does not exist
    elif click.confirm(f'{filepath} does not exist, create?'):

        with open(filepath, "w+"):
            pass
        file_config = process_yaml(filepath)
        main_app(BASE_PATH, filepath, file_config)
