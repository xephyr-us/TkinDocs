# TkinDocs 
## Overview
TkinDocs is a markup language frontend for Python's Tkinter package. This project enables a functioning GUI to be created using only a plaintext file. The user need never interact with the Tk widgets of which the GUI is made, though this functionality is present for users wishing to implement more complex user interfaces.

## Installation

TkinDocs may be installed using the following command:
```bash
pip install <packagename>
```
**Package yet to be uploaded to the Python Package Index*

TkinDocs is implemented exclusively using Python 3, and maintains a custom minimalist syntax. This project does not depend on XML, HTML, or any other preexisting markup language. This project's only dependency is Tkinter, a package with which most Python interpreters ship. 

If your interpreter did not come with Tkinter installed, run the following command to install it:

```bash
pip install tk
```

## Usage

TKinDocs' syntax and usage is described in detail in this project's `docs` directory

The `docs` directory contains  comprehensive documentation and several technical demos. This project's documentation will refer to a valid TkinDocs source as a TkinDoc (Tkinter Document). The language's syntax is described in detail in `docs/syntax.md`. Special widget arguments and options are described in `docs/options.md`.

## Contributing

Pull requests, forks, and contributions to this project are more than welcome. TkinDocs is designed such that individuals may easily modify or extend the language's syntax if they wish to.

The author of this project may be contacted for inquiry at `xavifmw@gmail.com`.

## License

Copyright (C) 2023 Xavier Mercerweiss

 This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
