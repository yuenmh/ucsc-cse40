import contextlib
import functools
import json
import os
import types
import unittest

import cse40.assignment
import cse40.autograder

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(THIS_DIR, "data")

CONFIG_PATH = os.path.join(DATA_DIR, 'autograder', 'config.json')
SUBMISSION_PATH = os.path.join(DATA_DIR, 'simple.py')

class TestAutograder(unittest.TestCase):
    def setUp(self):
        self._backup_send_request = cse40.autograder._send_request

    def tearDown(self):
        cse40.autograder._send_request = self._backup_send_request

    def test_history(self):
        cse40.autograder._send_request = functools.partial(_mock_history_response, self)

        arguments = types.SimpleNamespace(config_path = CONFIG_PATH,
                server = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        with contextlib.redirect_stdout(None):
            result = cse40.autograder._history(arguments)

        self.assertEquals(result, 0)

    def test_repeat(self):
        cse40.autograder._send_request = functools.partial(_mock_repeat_response, self)

        arguments = types.SimpleNamespace(config_path = CONFIG_PATH,
                server = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        with contextlib.redirect_stdout(None):
            result = cse40.autograder._repeat(arguments)

        self.assertEquals(result, 0)

    def test_submit(self):
        cse40.autograder._send_request = functools.partial(_mock_submit_response, self)

        arguments = types.SimpleNamespace(config_path = CONFIG_PATH,
                submission_path = SUBMISSION_PATH,
                server = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        with contextlib.redirect_stdout(None):
            result = cse40.autograder._submit(arguments)

        self.assertEquals(result, 0)

    def test_request_history(self):
        cse40.autograder._send_request = functools.partial(_mock_history_response, self)

        success, result = cse40.autograder.request_history(config_path = CONFIG_PATH,
                autograde_url = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        self.assertTrue(success)
        self.assertEquals(result, FAKE_HISTORY)

    def test_request_repeat(self):
        cse40.autograder._send_request = functools.partial(_mock_repeat_response, self)

        success, result = cse40.autograder.request_repeat(config_path = CONFIG_PATH,
                autograde_url = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        self.assertTrue(success)
        self.assertEquals(result, cse40.assignment.Assignment.from_dict(FAKE_ASSIGNMENT_JSON))

    def test_request_submit(self):
        cse40.autograder._send_request = functools.partial(_mock_submit_response, self)

        success, result = cse40.autograder.request_submit(config_path = CONFIG_PATH,
                submission_path = SUBMISSION_PATH,
                autograde_url = cse40.autograder.DEFAULT_AUTOGRADER_URL)

        self.assertTrue(success)
        self.assertEquals(result, cse40.assignment.Assignment.from_dict(FAKE_ASSIGNMENT_JSON))

def _mock_history_response(test_case, config, autograder_url):
    expected_config = dict(FAKE_CONFIG)
    expected_config['task'] = 'history'

    test_case.assertEquals(config, expected_config)
    test_case.assertEquals(autograder_url, cse40.autograder.DEFAULT_AUTOGRADER_URL)

    result = {'history': FAKE_HISTORY}
    return result, None

def _mock_repeat_response(test_case, config, autograder_url):
    expected_config = dict(FAKE_CONFIG)
    expected_config['task'] = 'repeat'

    test_case.assertEquals(config, expected_config)
    test_case.assertEquals(autograder_url, cse40.autograder.DEFAULT_AUTOGRADER_URL)

    result = {'assignment': FAKE_ASSIGNMENT_JSON}
    return result, None

def _mock_submit_response(test_case, config, autograder_url):
    expected_config = dict(FAKE_CONFIG)
    expected_config['task'] = 'submit'
    expected_config['code'] = FAKE_CODE

    test_case.assertEquals(config, expected_config)
    test_case.assertEquals(autograder_url, cse40.autograder.DEFAULT_AUTOGRADER_URL)

    result = {'assignment': FAKE_ASSIGNMENT_JSON}
    return result, None

def _load_config():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)

def _load_code():
    with open(SUBMISSION_PATH, 'r') as file:
        return file.read().strip()

FAKE_CONFIG = _load_config()
FAKE_CODE = _load_code()

FAKE_HISTORY = [
    {
        'id': '1',
        'score': [2, 3],
    },
    {
        'id': '4',
        'score': [5, 6],
    },
]

FAKE_ASSIGNMENT_JSON = {
    "name": "Hands-On 0: Getting Started",
    "start": "2023-03-31 12:17",
    "end": "2023-03-31 12:17",
    "questions": [
        {
            "name": "Q1",
            "max_points": 100,
            "timeout": 60,
            "score": 0,
            "message": "NotImplemented returned."
        },
        {
            "name": "Style",
            "max_points": 0,
            "timeout": 60,
            "score": 0,
            "message": "Style is clean!"
        }
    ]
}
