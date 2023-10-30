
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

from utils import is_tkinter_object, pull_from_dict


class TkGUI:
    """
    Encapsulates a GUI created using the tkinter framework
    """

    _INVALID_ROOT_OPTION_ERR_MSG = "Invalid option '{}' passed to root widget"

    def __init__(self, *args, **kwargs):
        self._named_widgets = {}
        self._root = tk.Tk(*args)
        self._config_root(kwargs)

    def __getitem__(self, item):
        try:
            return self._named_widgets[item]
        except KeyError:
            msg = f"{type(self).__name__} object contains no object of name {repr(item)}"
            raise KeyError(msg)

    def __setitem__(self, key, value):
        if is_tkinter_object(value):
            self._named_widgets[key] = value
        else:
            msg = f"Attempted to name non-tkinter object within {type(self).__name__} object"
            raise TypeError(msg)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __contains__(self, item):
        return item in self._named_widgets

    def _config_root(self, config):
        # Configures the root widget using the given 'config' dictionary
        valid_options = self._root.configure().keys()
        for key, value in config.items():
            if key not in valid_options:
                pull_from_dict(config, key)
                try:
                    func = getattr(self._root, key)
                    func(value)
                except AttributeError:
                    self._raise_invalid_root_option(key)
        self._root.configure(**config)

    def _raise_invalid_root_option(self, key):
        # Raises an error because the root was passed an invalid configuration option
        msg = self._INVALID_ROOT_OPTION_ERR_MSG.format(key)
        raise KeyError(msg)

    def start(self):
        """
        Starts the GUI's mainloop.
        :return: None
        """
        self._root.mainloop()

    def get_default(self, key, default=None):
        """
        Returns the value mapped to the given key if present, otherwise returns the given default value.
        :param key: The key mapped to the value to be returned
        :param default: The given default value; None if not specified
        :return: Either the value mapped to the given key, the given default value, or None
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def set_default(self, key, default=None):
        """
        Returns the value mapped to the given key if present, otherwise maps the given key to the given non-None
        default value.
        :param key: The key mapped to the value to be returned
        :param default: The given default value; None if not specified
        :return: Either the value mapped to the given key, the given default value, or None
        """
        value = self.get_default(key, default)
        if key is not None and value is not None:
            self.__setitem__(key, value)
        return value

    @property
    def root(self):
        """
        A readonly property for the root widget of the GUI.
        """
        return self._root
