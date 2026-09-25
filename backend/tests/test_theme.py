"""Tests unitarios para src/theme.py."""

import re

import pytest

import theme

COLOR_NAMES = [
    "DARK_BG",
    "PANEL_BG",
    "GRID_COLOR",
    "TEXT_COLOR",
    "ACCENT",
    "GREEN",
    "RED",
    "YELLOW",
    "PURPLE",
    "ORANGE",
]

HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")


@pytest.mark.parametrize("name", COLOR_NAMES)
def test_colors_are_hex_strings(name):
    assert HEX_COLOR.fullmatch(getattr(theme, name))


def test_colors_are_unique():
    values = [getattr(theme, name) for name in COLOR_NAMES]

    assert len(set(values)) == len(values)


def test_font_family_is_defined():
    assert theme.FONT_FAMILY == "monospace"
