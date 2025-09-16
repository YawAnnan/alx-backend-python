#!/usr/bin/env python3
"""
Utility functions for the project.
"""


def access_nested_map(nested_map, path):
    """
    Access a nested map using a sequence of keys.

    Args:
        nested_map (dict): The nested dictionary to traverse.
        path (tuple): A tuple of keys representing the path.

    Returns:
        The value found at the end of the path.

    Example:
        >>> access_nested_map({"a": {"b": 2}}, ("a", "b"))
        2
    """
    current = nested_map
    for key in path:
        current = current[key]
    return current
