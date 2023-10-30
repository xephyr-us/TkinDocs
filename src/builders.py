
# Copyright (C) 2023 Xavier Francis Mercerweiss
# The author of this software may be contacted at <xavifmw@gmail.com>

# This file is part of TkinDocs.

# TkinDocs is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# TkinDocs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with TkinDocs.
# If not, see <https://www.gnu.org/licenses/>


import abc
from collections import deque
import tkinter as tk
from tkinter import ttk

from .errors import DuplicateRootError, AbsentRootError, InvalidParentError
from .gui import TkGUI
from utils import pull_from_dict


class Builder(abc.ABC):
    """
    Describes an interface used to maintain a stack of Tk widgets and return a finished product.
    """

    @abc.abstractmethod
    def open_widget(self, WidgetType, *args, **kwargs):
        """
        Creates a widget of WidgetType, passes the given arguments to its constructor, then pushes the widget onto the
        widget stack.
        """
        pass

    @abc.abstractmethod
    def close_widget(self, layout_name, *args, **kwargs):
        """
        Attaches the top-most widget to its parent using a method of name 'layout_name', passes the given arguments
        to said method, then pulls said widget from the widget stack.
        """
        pass

    @abc.abstractmethod
    def finalize_gui(self):
        """
        Returns some object encapsulating a usable GUI object, created using the widget stack.
        """
        pass

    @property
    @abc.abstractmethod
    def gui(self):
        """
        A readonly property for the GUI object held by the Builder.
        """
        pass


class TkGUIBuilder(Builder):
    """
    Implements the Builder interface such that a TkGUI object may be constructed.
    """

    LAYOUT_KEY = "layout"
    WIDGET_NAME_KEY = "key"
    VAR_NAME_KEY = "var_key"

    _DEFAULT_LAYOUT = "pack"

    _INVALID_PARENT_ERR_MSG = "{} object attempted to create widget without a suitable parent"
    _ABSENT_ROOT_ERR_MSG = "{} object attempted to create TkGUI without root widget"
    _DUPLICATE_ROOT_ERR_MSG = "{} object attempted to create root widget inside of active root widget"

    def __init__(self):
        self._LAYOUT_CONFIGS = {
            "grid": self._grid_config
        }
        self._WIDGET_INITS = {
            tk.Tk:          self._init_root,
            tk.Radiobutton: self._init_radiobutton,
            tk.Checkbutton: self._init_checkbutton,
            ttk.Combobox:   self._init_combobox,
        }
        self._widget_stack = None
        self._current = None
        self._parent = None
        self._gui = None
        self._init_attributes()

    def _init_attributes(self):
        # Initializes instance attributes
        self._widget_stack = deque()
        self._current = None
        self._parent = None
        self._gui = None

    def _init_root(self, args, kwargs):
        # Creates a new root widget, performs some error checking
        if self._current is not None:
            self._raise_duplicate_root_error()
        self._gui = TkGUI(*args, **kwargs)
        return self._gui.root

    def _init_radiobutton(self, args, kwargs):
        # Creates a new radiobutton widget
        int_var = self._get_var(kwargs, tk.IntVar)
        radio = tk.Radiobutton(self._current, *args, **kwargs, variable=int_var)
        return radio

    def _init_checkbutton(self, args, kwargs):
        # Creates a new checkbutton widget
        int_var = self._get_var(kwargs, tk.IntVar)
        check = tk.Checkbutton(self._current, *args, **kwargs, variable=int_var)
        return check

    def _init_combobox(self, args, kwargs):
        # Creates a new combobox widget
        str_var = self._get_var(kwargs, tk.StringVar)
        combo = ttk.Combobox(self._current, *args, **kwargs, textvariable=str_var)
        combo["state"] = "readonly"
        return combo

    def _init_widget(self, WidgetType, args, kwargs):
        # Creates a new instance of an arbitrary widget
        return WidgetType(self._current, *args, **kwargs)

    def _grid_config(self, _, kwargs):
        # Configures a widget's parent for grid layout usage
        row = kwargs["row"]
        column = kwargs["column"]
        rowspan = kwargs["rowspan"] if "rowspan" in kwargs else 1
        columnspan = kwargs["columnspan"] if "columnspan" in kwargs else 1
        column_start, row_start = self._parent.grid_size()
        row_stop = row + rowspan
        column_stop = column + columnspan
        for y in range(row_start, row_stop):
            self._parent.rowconfigure(y, weight=1)
        for x in range(column_start, column_stop):
            self._parent.columnconfigure(x, weight=1)

    def _raise_invalid_parent_error(self):
        # Raises an error because the current widget's parent is invalid
        msg = self._INVALID_PARENT_ERR_MSG.format(type(self).__name__)
        raise InvalidParentError(msg)

    def _raise_absent_root_error(self):
        # Raises an error because no root widget exists
        msg = self._ABSENT_ROOT_ERR_MSG.format(type(self).__name__)
        raise AbsentRootError(msg)

    def _raise_duplicate_root_error(self):
        # Raises an error because a root exists inside another root
        msg = self._DUPLICATE_ROOT_ERR_MSG.format(type(self).__name__)
        raise DuplicateRootError(msg)

    def _create_widget_of_type(self, WidgetType, args, kwargs):
        # Dispatches widget creation method based on WidgetType
        if WidgetType in self._WIDGET_INITS:
            init = self._WIDGET_INITS[WidgetType]
            return init(args, kwargs)
        return self._init_widget(WidgetType, args, kwargs)

    def _name_object(self, obj, name):
        # Saves a reference to the given object as a key-value pair within the current TKGUI object
        if name is not None:
            self._gui[name] = obj

    def _get_var(self, kwargs, default):
        # Pulls the 'VAR_NAME_KEY' argument from kwargs; returns the existing variable of that name if it exists,
        # otherwise creates one and saves it as a key-value pair within the current TkGUI object
        var_name = pull_from_dict(kwargs, self.VAR_NAME_KEY)
        var = self._gui.set_default(var_name, default())
        return var

    def _perform_layout_config(self, layout, args, kwargs):
        # Dispatches layout configuration, if needed, based on the layout's name
        if layout in self._LAYOUT_CONFIGS:
            config = self._LAYOUT_CONFIGS[layout]
            config(args, kwargs)

    def _push_to_stack(self, value):
        # Pushes the given value to the widget stack
        if self._parent is not None:
            self._widget_stack.append(self._parent)
        self._parent = self._current
        self._current = value

    def _pull_from_stack(self):
        value = self._current
        # Pulls the topmost value from the widget stack
        self._current = self._parent
        self._parent = self._widget_stack.pop() if len(self._widget_stack) > 0 else None
        return value

    def open_widget(self, WidgetType, *args, **kwargs):
        """
        Creates a new widget of the given type and pushes it onto the widget stack.
        :param WidgetType: The type of the widget to be created
        :param args: A set of arbitrary positional arguments to be passed to the widget's constructor
        :param kwargs: A set of arbitrary keyword arguments to be passed to the widget's constructor
        :return: None
        """
        if WidgetType is not tk.Tk and self._current is None:
            self._raise_invalid_parent_error()
        name = pull_from_dict(kwargs, self.WIDGET_NAME_KEY)
        widget = self._create_widget_of_type(WidgetType, args, kwargs)
        self._name_object(widget, name)
        self._push_to_stack(widget)

    def close_widget(self, *args, **kwargs):
        """
        Attaches the top-most widget to its parent using a specified method.
        :param args: A set of arbitrary positional arguments to be passed to the widget's attachment method
        :param kwargs: A set of arbitrary keyword arguments to be passed to the widget's attachment method; may include
        the 'layout' keyword argument to specify an attachment method
        :return: None
        """
        if self._parent is None:
            gui = self._gui
            self._init_attributes()
            self._gui = gui
        else:
            layout = pull_from_dict(kwargs, self.LAYOUT_KEY, default=self._DEFAULT_LAYOUT)
            self._perform_layout_config(layout, args, kwargs)
            method = getattr(self._current, layout)
            method(*args, **kwargs)
            self._pull_from_stack()

    def finalize_gui(self):
        """
        Closes all open widgets with default arguments, then returns a finished TkGUI object.
        :return: A usable TKGUI object
        """
        if self._gui is None:
            self._raise_absent_root_error()
        while self._parent is not None:
            self.close_widget()
        gui = self._gui
        self._init_attributes()
        return gui

    @property
    def gui(self):
        return self._gui
