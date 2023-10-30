
# Copyright (C) 2023 Xavier Francis Mercerweiss
# The author of this software may be contacted at <xavifmw@gmail.com>

# This file is part of TkinDocs.

# TkinDocs is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# TkinDocs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with TkinDocs.
# If not, see <https://www.gnu.org/licenses/>


import tkinter as tk


def pull_from_dict(d, key, default=None):
    """
    Removes a key-value pair from a dictionary if the given key is present; otherwise returns a default value
    :param d: A dictionary
    :param key: A key to be pulled
    :param default: A default value; None if not specified
    :return: Either a value matching the given key, the given default value, or None
    """
    if key in d:
        value = d[key]
        del d[key]
        return value
    return default


def is_tkinter_object(obj):
    """
    Determines whether a given object exists within the 'tkinter' module
    :param obj: An object to be tested
    :return: True if the given object exists within the 'tkinter' module, False otherwise
    """
    return obj.__module__ == tk.__name__
