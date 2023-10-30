
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


class Parser(abc.ABC):
    """
    Describes the interface and shared implementation used to parse a TkinDoc.
    """

    _WIPED = "\n\t"

    def __init__(self, content, reserved):
        """
        Initializes a reusable parser object.
        :param content: The content to be parsed
        :param reserved: A set of reserved characters designating the start of tags
        """
        self._content = content
        self._reserved = set(reserved)

    def __iter__(self):
        text = self._get_text_from_content()
        parsable = self._process_text(text)
        gen = self._get_text_parse_generator(parsable)
        return gen

    def _process_text(self, text):
        # Processes the given text such that it is parsable; currently collapses tabs and newlines
        current = text
        for ch in self._WIPED:
            current = current.replace(ch, "")
        return current

    def _get_text_parse_generator(self, text):
        # Defines the parsing algorithm used to split the given text into a set of tags; returns a generator object
        # implementing this algorithm
        stripped = text.strip()
        output = ""
        for ch in stripped:
            if ch in self._reserved and output != "":
                yield output.strip()
                output = ""
            output += ch
        yield output

    @abc.abstractmethod
    def _get_text_from_content(self):
        """
        Retrieves usable text from the given content.
        """
        pass


class TKDFileParser(Parser):

    def _get_text_from_content(self):
        # Given that the parser's content is the path to a valid plaintext file, retrieve the content's text
        with open(self._content, "r") as i:
            return i.read()


class TKDStringParser(Parser):

    def _get_text_from_content(self):
        # Given that the parser's content is a string, return the string
        return self._content
