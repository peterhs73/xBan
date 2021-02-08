#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os
import logging
from xban.style import TILE_STYLE
import random

"""Interaction with yaml files"""

io_logger = logging.getLogger("xban-io")


def xban_content(filepath, yaml_stream):
    """Check and correct yaml_stream into the correct xban format

    this function is used within process_yaml function
    There are several scenarios:
    - File is empty (directly passed from the xban create)
    - File is a yaml file but is not valid xban yaml
    - File is a valid xban yaml file but not a xban file
    - File is a xban file
    :param filepath str: yaml filepath
    :param yaml_stream: yaml read stream
    """
    filename = os.path.basename(os.path.splitext(filepath)[0])
    xban_config_default = {
        "xban_config": {"title": filename, "description": "", "board_color": [],}
    }
    if yaml_stream:
        if not all(isinstance(page, dict) for page in yaml_stream):
            io_logger.error(f"{filepath} does not have a valid xban format")
            return []
        elif "xban_config" in yaml_stream[0]:
            return yaml_stream
        elif len(yaml_stream) >= 2:
            io_logger.error(f"{filepath} have too many yaml documents")
            return []
        else:
            # if the yaml file does not have the configuration
            # check the length and add the color
            content_len = len(yaml_stream[0])
            color = random.sample(TILE_STYLE.keys(), content_len)
            xban_config_default["xban_config"]["board_color"].extend(color)
            return [xban_config_default, yaml_stream[0]]
    else:
        return [xban_config_default, {}]


def process_yaml(filepath):
    """Process yaml file

    if the file cannot be opened, an error will be logged
    the detailed file processing see xban_content()
    """
    print("fisss", filepath)
    try:
        with open(filepath, "r") as f:
            yaml_stream = list(yaml.load_all(f, Loader=yaml.SafeLoader))

        return xban_content(filepath, yaml_stream)
    except Exception as e:
        io_logger.error(f"Incorrect {filepath}. Error: {str(e)}")
        return []


def save_yaml(filepath, xban_content):
    """Save the xban configuration to yaml format"""
    try:
        with open(filepath, "w+") as f:
            yaml.safe_dump_all(
                xban_content, f, default_flow_style=False, sort_keys=False
            )
    except Exception as e:
        io_logger.error(f"Cannot save {filepath}. Error: {str(e)}")
