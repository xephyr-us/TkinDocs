
# Copyright (C) 2023 Xavier Francis Mercerweiss
# The author of this software may be contacted at <xavifmw@gmail.com>

# This file is part of TkinDocs.

# TkinDocs is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# TkinDocs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with TkinDocs.
# If not, see <https://www.gnu.org/licenses/>


class InvalidWidgetError(Exception):
    """
    Denotes that the program attempted to create an invalid widget
    """
    pass


class InvalidParentError(Exception):
    """
    Denotes that the program attempted to attach a widget to an invalid parent widget
    """
    pass


class AbsentRootError(Exception):
    """
    Denotes that the program attempted to create a widget without a suitable root widget
    """
    pass


class DuplicateRootError(Exception):
    """
    Denotes that the program attempted to create a root widget within another root widget
    """
    pass


class IncoherentArgumentError(Exception):
    """
    Denotes that the program was passed a syntactically incorrect argument
    """
    pass
