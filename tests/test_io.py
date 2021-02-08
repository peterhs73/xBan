#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Test xban yaml file processing and saving"""

import yaml
from xban.io import xban_content, process_yaml
from xban.style import TILE_STYLE
import logging
from unittest.mock import patch, mock_open


def test_empty():
    """Test when the input string is empty"""
    default = [
        {"xban_config": {"title": "testfile", "description": "", "board_color": [],}},
        {},
    ]

    assert default == xban_content("test/testfile.yaml", [])


def test_invalid_xban(caplog):
    """Test when the yaml stream is invalid"""

    # first is a valid dict but the second one is not
    stream = [{"config": {"test": "new"}}, []]
    assert xban_content("test/testfile.yaml", stream) == []
    assert caplog.record_tuples == [
        (
            "xban-io",
            logging.ERROR,
            "test/testfile.yaml does not have a valid xban format",
        )
    ]


def test_invalid_xban(caplog):
    """Test when the yaml stream is invalid"""

    # first is a valid dict but the second one is not
    stream = [{"config": {"test": "new"}}, []]
    assert xban_content("test/testfile.yaml", stream) == []
    assert caplog.record_tuples == [
        (
            "xban-io",
            logging.ERROR,
            "test/testfile.yaml does not have a valid xban format",
        )
    ]


def test_valid_xban():
    """Test when the yaml stream is a valid xban format"""

    # first is a valid dict but the second one is not
    stream = [
        {"xban_config": {"title": "testfile", "description": "", "board_color": [],}},
        {},
    ]
    assert xban_content("test/testfile.yaml", stream) == stream


def test_valid_yaml_xban(caplog):
    """Test when the yaml stream is a valid yaml file"""

    # the color generation is random so need to check individual values

    stream = [{"new": ["a", "b"], "old": ["c", "d"]}]

    parsed = xban_content("test/testfile.yaml", stream)
    assert parsed[1] == stream[0]
    assert parsed[0]["xban_config"]["title"] == "testfile"

    color = parsed[0]["xban_config"]["board_color"]

    assert len(color) == 2
    assert color[0] in TILE_STYLE


def test_multi_docs_stream(caplog):
    """Test when yaml file has too many documents"""
    stream = [{"new": ["a", "b"], "old": ["c", "d"]}, {"new": ["a", "b"]}]
    assert xban_content("test/testfile.yaml", stream) == []
    assert caplog.record_tuples == [
        ("xban-io", logging.ERROR, "test/testfile.yaml have too many yaml documents",)
    ]


def test_process_yaml_invalid(caplog):
    """Test given process yaml given a mocked io and invalid input"""
    data = """
    text_key: incorrect format
    - listitem
    - listitem
    """

    with patch("builtins.open", mock_open(read_data=data)):
        result = process_yaml("test/file.yaml")

    for record in caplog.records:
        assert (
            "Incorrect test/file.yaml. Error: while parsing a block mapping"
            in record.message
        )
        assert record.levelname == "ERROR"
    assert result == []


DATA = """
xban_config:
    title: testfile
    description: test io
    board_color:
        - red
        - teal
---
todo:
    - need more tests!
    - and more!
finished:
    - io tests
"""


def test_process_yaml_valid(caplog):
    """Test given process yaml given a mocked io"""

    with patch("builtins.open", mock_open(read_data=DATA)):
        result = process_yaml("test/testfile.yaml")
    assert result == [
        {
            "xban_config": {
                "title": "testfile",
                "description": "test io",
                "board_color": ["red", "teal"],
            }
        },
        {"todo": ["need more tests!", "and more!"], "finished": ["io tests"],},
    ]
