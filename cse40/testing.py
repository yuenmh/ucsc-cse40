"""Simplified testing framework for CSE 40.

This module provides a simple framework for testing your code. If you are familiar
with the `pytest` library, this will be very familiar.
"""

import functools
import importlib
import inspect
import traceback
import typing

import cse40.question


_TEST_FLAG = "__cse40_test__"


class TestFile(cse40.question.Question):
    """A test file that runs tests on a submission."""

    def __init__(self, module_name: str):
        self.module_name = module_name

    def grade(self, submission, additional_data={}, show_exceptions=False):
        try:
            mod = importlib.import_module(self.module_name)
        except ImportError:
            self.fail(f"Could not import module `{self.module_name}`.")
            return 0

        fns = (
            fn 
            for fn in (getattr(mod, name) for name in dir(mod)) 
            if callable(fn) and hasattr(fn, _TEST_FLAG)
        )
        for fn in fns:
            # Finding args the function needs
            param_names = inspect.signature(fn).parameters.keys()
            kwargs = {}
            for name in param_names:
                if name == "submission":
                    kwargs[name] = submission
                elif name in additional_data:
                    kwargs[name] = additional_data[name]
                else:
                    self.fail(
                        f"Test `{fn.__name__}` requires parameter `{name}`, "
                        "but it is not present in `additional_data`."
                    )
                    return 0
            # Running the test
            try:
                fn(**kwargs)
            except Exception as _:
                if show_exceptions:
                    traceback.print_exc()
                self.fail(f"Test `{fn.__name__}` failed.")

        # Maybe we can return a score based on how many tests passed?
        return 1


def test(fn: typing.Callable[..., None]) -> typing.Callable[..., None]:
    """Decorator to mark a function as a test."""
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        fn(*args, **kwargs)

    setattr(fn, _TEST_FLAG, None)
    return inner

