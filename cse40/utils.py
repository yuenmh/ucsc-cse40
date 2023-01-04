import atexit
import importlib
import json
import multiprocessing
import os
import shutil
import sys
import tempfile
import traceback
import uuid

import cse40.ipynbimport

REAP_TIME_SEC = 5

class Mock(object):
    def __init__(self):
        self.item_history = list()
        self.attribute_history = list()
        self.call_history = list()

    def __repr__(self):
        return "Mock -- Item History: %s, Attribute History: %s, Call History: %s" % (str(self.item_history), str(self.attribute_history), str(self.call_history))

    def __call__(self, *args, **kwargs):
        self.call_history.append((args, kwargs))
        return self

    def __getitem__(self, name):
        self.item_history.append(name)
        return self

    def __getattr__(self, name):
        self.attribute_history.append(name)
        return self

def _invoke_helper(queue, function):
    value = None
    error = None

    try:
        value = function()
    except Exception as ex:
        error = (ex, traceback.format_exc())

    sys.stdout.flush()

    queue.put((value, error))
    queue.close()

# Return: (success, function return value)
# On timeout, success will be false and the value will be None.
# On error, success will be false and value will be the string stacktrace.
# On suesssful completion, sucess will be true and value may be None (if nothing was returned).
def invoke_with_timeout(timeout, function):
    queue = multiprocessing.Queue(1)
    invoke_helper = lambda: _invoke_helper(queue, function)

    # Note that we use processes instead of threads so they can be more completely killed.
    process = multiprocessing.Process(target = invoke_helper)
    process.start()

    # Wait for at most the timeout.
    process.join(timeout)

    # Check to see if the thread is still running.
    if process.is_alive():
        # Kill the long-running thread.
        process.terminate()

        # Try to reap the thread once before just giving up on it.
        process.join(REAP_TIME_SEC)

        return (False, None)

    # Check to see if the process explicitly existed (like via sys.exit()).
    if (queue.empty()):
        return (False, 'Code explicitly exited (like via sys.exit()).')

    value, error = queue.get()

    if (error is not None):
        exception, stacktrace = error
        return (False, stacktrace)

    return (True, value)

def prepare_submission(path):
    """
    Get a submission from a path (to either a notebook or vanilla python).
    """

    submission = None

    if (path.endswith('.ipynb')):
        submission = cse40.ipynbimport.load_from_path(path)
    elif (path.endswith('.py')):
        spec = importlib.util.spec_from_file_location("submission", path)
        submission = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(submission)
    else:
        raise ValueError("Unknown extension for submission: '%s'." % (path))

    return submission

def extract_notebook_code(path):
    """
    Extract all the code cells from an iPython notebook.
    A concatenation of all the cells (with a newline between each cell) will be output.
    """

    with open(path, 'r') as file:
        notebook = json.load(file)

    contents = []

    for cell in notebook['cells']:
        if (cell['cell_type'] != 'code'):
            continue

        contents.append((''.join(cell['source'])))

    return "\n".join(contents)

def get_temp_path(prefix = '', suffix = '', rm = True):
    """
    Get a path to a valid temp dirent.
    If rm is True, then the dirent will be attempted to be deleted on exit (no error will ocurr if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + str(uuid.uuid4()) + suffix)

    if (rm):
        atexit.register(remove_dirent, path)

    return path

def remove_dirent(path):
    if (not os.path.exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError("Unknown type of dirent: '%s'." % (path))
