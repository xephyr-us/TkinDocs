
# Copyright (C) 2023 Xavier Francis Mercerweiss
# The author of this software may be contacted at <xavifmw@gmail.com>

# This file is part of TkinDocs.

# TkinDocs is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# TkinDocs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with TkinDocs.
# If not, see <https://www.gnu.org/licenses/>


from functools import partial
import importlib as ilib
from os import path
import tkinter as tk
from tkinter import ttk

from .builders import TkGUIBuilder
from .errors import InvalidWidgetError, IncoherentArgumentError
from .parsers import TKDFileParser, TKDStringParser


class TkGUIFactory:
    """
    Converts a TkinDoc into a usable TKGUI object.
    """

    _RESERVED = r"\/|,$"
    _BOOLEANS = {"True", "False"}

    _ASSIGNMENT_TOKEN = "="
    _OPEN_LIST_TOKEN = "{"
    _CLOSE_LIST_TOKEN = "}"
    _REFERENCE_TOKEN = "?"
    _SELF_REFERENCE_TOKEN = "??"

    _PATH_DELIMITER = "."
    _LIST_DELIMITER = ":"

    _IMPORT_KEYWORD = "import"

    _WIDGETS = {
        "root":   tk.Tk,
        "frame":  tk.Frame,
        "label":  tk.Label,
        "entry":  tk.Entry,
        "text":   tk.Text,
        "canvas": tk.Canvas,
        "button": tk.Button,
        "radio":  tk.Radiobutton,
        "check":  tk.Checkbutton,
        "combo":  ttk.Combobox
    }

    _INVALID_WIDGET_ERR_MSG = "Invalid widget tag '{}', please check TkinDoc source"
    _INCOHERENT_ARG_ERR_MSG = "Attempted to process argument in inappropriate position" \
                              ", please check TkinDoc source"
    _RELATIVE_IMPORT_ERR_MSG = "Attempted to perform relative import; TkinDocs does not support relative imports"

    def __init__(self):
        self._TAG_DISPATCH = {
            "\\": self._process_opener,
            "/": self._process_closer,
            "|": self._process_singlet,
            "$": self._process_call,
            ",": self._process_argument
        }
        self._imported = {}
        self._builder = TkGUIBuilder()
        self._args = self._kwargs = self._teardown = None
        self._init_arguments()

    def _init_arguments(self):
        # Initializes teardown arguments
        self._args = []
        self._kwargs = {}

    def _process_opener(self, *args):
        # Processes an opening tag
        self._call_teardown()
        widget_name = args[0].lower()
        WidgetType = self._get_widget_type(widget_name)
        self._teardown = partial(self._open_widget_of_type, WidgetType)

    def _process_closer(self, *_):
        # Processes a closing tag
        self._call_teardown()
        self._teardown = self._close_current_widget

    def _process_singlet(self, *args):
        # Processes a single-line tag
        self._call_teardown()
        widget_name = args[0]
        WidgetType = self._get_widget_type(widget_name)
        self._teardown = partial(self._open_and_close_widget_of_type, WidgetType)

    def _process_argument(self, *args):
        # Processes an argument tag
        arg = args[0]
        if self._teardown is None:
            self._raise_incoherent_argument_error()
        if self._ASSIGNMENT_TOKEN in arg:
            key, value = arg.split(self._ASSIGNMENT_TOKEN)
            self._kwargs[key] = self._evaluate(value)
        else:
            self._args.append(self._evaluate(arg))

    def _process_call(self, *args):
        # Processes a function call tag
        func_name, *sent = args[0].split()
        if func_name == self._IMPORT_KEYWORD:
            received = (x for x in sent if x != "as")
            self._import_module(*received)
        else:
            func = self._deference_function(func_name)
            self._teardown = func

    def _raise_invalid_widget_error(self, widget_tag):
        # Raises an error the source contained an invalid widget tag
        msg = self._INVALID_WIDGET_ERR_MSG.format(widget_tag)
        raise InvalidWidgetError(msg)

    def _raise_incoherent_argument_error(self):
        # Raises an error because an argument tag was syntactically incorrect
        msg = self._INCOHERENT_ARG_ERR_MSG
        raise IncoherentArgumentError(msg)

    def _raise_relative_import_error(self):
        # Raises an error because a relative import was attempted
        msg = self._RELATIVE_IMPORT_ERR_MSG
        raise ModuleNotFoundError(msg)

    def _dispatch_parser(self, content):
        # Dispatches the type of parser to be created based on the properties of the source content
        if path.exists(content):
            return TKDFileParser(content, self._RESERVED)
        return TKDStringParser(content, self._RESERVED)

    def _call_teardown(self):
        # Calls the current teardown function if valid
        if self._teardown is not None:
            self._teardown(*self._args, **self._kwargs)
            self._init_arguments()

    def _get_widget_type(self, name):
        # Converts a widget name into a widget type if valid
        try:
            return self._WIDGETS[name]
        except KeyError:
            self._raise_invalid_widget_error(name)

    def _open_widget_of_type(self, WidgetType, *args, **kwargs):
        # Open a widget of the given type
        self._builder.open_widget(WidgetType, *args, **kwargs)

    def _close_current_widget(self, *args, **kwargs):
        # Close the current widget
        self._builder.close_widget(*args, **kwargs)

    def _open_and_close_widget_of_type(self, WidgetType, *args, **kwargs):
        # Open a widget of the given type, then close it; divide the given arguments between the opener and the closer
        # based on the position of the 'layout' argument
        open_kwargs = {}
        close_kwargs = {}
        current = open_kwargs
        for k, v in kwargs.items():
            if k == self._builder.LAYOUT_KEY:
                current = close_kwargs
            current[k] = v
        self._builder.open_widget(WidgetType, *args, **open_kwargs)
        self._builder.close_widget(**close_kwargs)

    def _evaluate(self, value):
        # Convert the given string into an appropriate data type given its properties
        stripped = value.strip()
        if stripped.startswith(self._SELF_REFERENCE_TOKEN):
            start = len(self._SELF_REFERENCE_TOKEN)
            func = self._deference_function(stripped[start:])
            return partial(func, self._builder.gui)
        elif stripped.startswith(self._REFERENCE_TOKEN):
            start = len(self._REFERENCE_TOKEN)
            return self._deference_function(stripped[start:])
        if stripped.startswith(self._OPEN_LIST_TOKEN) and stripped.endswith(self._CLOSE_LIST_TOKEN):
            return self._to_list(stripped)
        elif stripped in self._BOOLEANS:
            return bool(stripped)
        elif stripped.isnumeric():
            return float(stripped) if "." in stripped else int(stripped)
        return stripped.strip("\"")

    def _import_module(self, name, alias=None):
        # Import the given module
        if name.startswith(self._PATH_DELIMITER):
            self._raise_relative_import_error()
        module = ilib.import_module(name, __name__)
        key = name.split(self._PATH_DELIMITER)[-1] if alias is None else alias
        self._imported[key] = name, module

    def _deference_function(self, name):
        # Dereference a function using its name as listed within the TkinDoc
        module_name, func_name = name.split(self._PATH_DELIMITER)
        _, module = self._imported[module_name]
        func = getattr(module, func_name)
        return func

    def _to_list(self, value):
        # Convert a given string into a list based on the TkinDoc list syntax
        start = len(self._OPEN_LIST_TOKEN)
        stop = -len(self._CLOSE_LIST_TOKEN)
        values = value[start:stop].split(self._LIST_DELIMITER)
        return tuple(self._evaluate(x) for x in values)

    def to_gui(self, content):
        """
        Convert a TkinDoc into a functioning TkGUI object.
        :param content: The TkinDoc to be converted
        :return: A functioning TkGUI object
        """
        parser = self._dispatch_parser(content)
        for tag in parser:
            symbol, value = tag[0], tag[1:].strip()
            method = self._TAG_DISPATCH[symbol]
            method(value)
        self._call_teardown()
        return self._builder.finalize_gui()
