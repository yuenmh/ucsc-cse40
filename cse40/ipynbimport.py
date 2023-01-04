"""
This file contains code for selectively executing parts of an ipython/jupyter
notebook
 - import statements
 - class definitions
 - function definitions

Its purpose is to assist the use of python notebooks for homework assignments,
where code can be unit-tested for automatic feedback to students.

Note that, while one could use this code to run imported code in a weak sandbox
by limiting the __builtin__ functions in the evaluation namespace (e.g., as in
https://github.com/zopefoundation/RestrictedPython), a preferred approach is to
run the unittesting process in a namespace jail (e.g., using
https://github.com/google/nsjail, https://github.com/netblue30/firejail,
https://github.com/containers/bubblewrap).

This code was adapted from `ipynb` (https://github.com/ipython/ipynb), as
licensed under the BSD-3-Clause License, and re-released under the same:

################################################################################
BSD 3-Clause License

Copyright (c) 2022, Reilly Raab
Copyright (c) 2016, Yuvi Panda
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import sys
import json
import ast
import types
import linecache
import traceback

from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

ALLOWED_NODES = set([ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef])

INJECTED_CODE = [""]


def inject_code(code):
    INJECTED_CODE[0] = code


def get_injected_code():
    return INJECTED_CODE[0]


def filter_ast(module_ast):
    """
    Filters a given module ast, removing non-whitelisted nodes

    It allows only the following top level items:
     - imports
     - function definitions
     - class definitions
     - top level assignments where all the targets on the LHS are all caps
    """

    def node_predicate(node):
        """
        Return true if given node is whitelisted
        """
        for an in ALLOWED_NODES:
            if isinstance(node, an):
                return True

        # Recurse through Assign node LHS targets when an id is not specified,
        # otherwise check that the id is uppercase
        if isinstance(node, ast.Assign):
            return all(
                [node_predicate(t) for t in node.targets if not hasattr(t, "id")]
            )

        return False

    module_ast.body = [n for n in module_ast.body if node_predicate(n)]
    return module_ast


def filter_cells(nb):
    """
    nb is passed in as a dictionary (ipynb source parsed as JSON)
    return string of concatenated code cells
    """
    source = ""
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            # transform the input to executable Python
            source += "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            source += "\n# " + "# ".join(cell["source"])
        # We want a blank newline after each cell's output.
        # And the last line of source doesn't have a newline usually.
        source += "\n\n"
    return source


def extract_source(path):
    """
    get source of .ipynb file by file path
    """

    with open(path) as f:
        try:
            nb = json.load(f)
        except ValueError:
            # This is if it isn't a valid JSON file at all
            raise ImportError(f"Could not import {path}: ipynb file is not valid JSON")

    return filter_cells(nb)


def load_ipynb(extracted_source, module_filename=None):
    """
    execute the extracted source code:
     - if module_filename is None, return the abstract syntax tree
     - otherwise, execute in a new namespace dictionary
    """

    filtered_ast = filter_ast(ast.parse(extracted_source))

    if module_filename is None:
        return filtered_ast
    else:

        env = {}

        try:
            exec(compile(filtered_ast, filename=module_filename, mode="exec"), env)
        except Exception as e:
            traceback.print_exc()
            exit(1)

        return env


################################################################################
# Simple function to load as namespace
################################################################################


def load_from_path(path):

    extracted_source = extract_source(path)

    env = load_ipynb(extracted_source, "<ipynb>")

    ns = types.SimpleNamespace(**env)

    return ns


################################################################################
# hook into python import system
################################################################################


class IPynbFinder(MetaPathFinder):
    """
    Finder for ipynb files.

    Allows us to do "import xyz" when referring to "xyz.ipynb"

    The loader_class passed in to the constructor is used to do actual loading.

    https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder
    """

    def __init__(self, loader_class):
        self.loader_class = loader_class

    def find_spec(self, fullname, path, target=None):

        path = f"{fullname}.ipynb"

        origin_redirect = "_" + path

        if os.path.exists(path):
            return ModuleSpec(
                name=fullname,
                loader=self.loader_class(),
                origin=origin_redirect,
            )


class FilteredLoader(Loader):
    def exec_module(self, module):

        origin_redirect = module.__spec__.origin
        path = origin_redirect[1:]

        extracted_source = extract_source(path)

        linecache.cache[origin_redirect] = (
            len(extracted_source),
            None,
            extracted_source.splitlines(keepends=True),
            origin_redirect,
        )

        env = load_ipynb(extracted_source, path)

        module.__dict__.update(env)

    def create_module(self, spec):
        return None


sys.meta_path.append(IPynbFinder(FilteredLoader))
