"""
An interface for interacting with the autograder (submitting assignments, querying scores, etc.).
"""

import argparse
import json
import sys
import urllib.request

import cse40.assignment
import cse40.code

ENCODING = 'utf-8'
DEFAULT_CONFIG_PATH = 'config.json'
DEFAULT_SUBMISSION_PATH = 'assignment.ipynb'
DEFAULT_AUTOGRADER_URL = 'http://sozopol.soe.ucsc.edu:12345'

TASK_SUBMIT = 'submit'
TASK_REPEAT = 'repeat'
TASKS = [TASK_SUBMIT, TASK_REPEAT]

def submit_notebook(config_path = DEFAULT_CONFIG_PATH, submission_path = DEFAULT_SUBMISSION_PATH,
        autograde_url = DEFAULT_AUTOGRADER_URL):
    source_code = cse40.code.extract_code(submission_path)

    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = 'grade'
    config['code'] = source_code

    payload = bytes(json.dumps(config), ENCODING)
    raw_response = urllib.request.urlopen(autograde_url, data = payload)

    status = raw_response.status
    if (status != 200):
        print("Got a failure status from the autograding server: %s." % (status))
        return None

    body = json.loads(raw_response.read().decode(encoding = ENCODING))

    if (body['status'] != 'success'):
        return (False, body['message'])

    return (True, cse40.assignment.Assignment.from_dict(body['assignment']))

def submit(arguments):
    (success, result) = submit_notebook(arguments.config_path, arguments.submission_path,
            arguments.server)

    if (not success):
        print('The autograder failed to grade your assignment.')
        print('Message from the autograder: ' + result)
        return 1

    print('The autograder successfully graded your assignment.')
    print(result.report())

    return 0

def request_repeat(config_path = DEFAULT_CONFIG_PATH, autograde_url = DEFAULT_AUTOGRADER_URL):
    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = 'repeat'

    payload = bytes(json.dumps(config), ENCODING)
    raw_response = urllib.request.urlopen(autograde_url, data = payload)

    status = raw_response.status
    if (status != 200):
        print("Got a failure status from the autograding server: %s." % (status))
        return None

    body = json.loads(raw_response.read().decode(encoding = ENCODING))

    if (body['status'] != 'success'):
        return (False, body['message'])

    return (True, cse40.assignment.Assignment.from_dict(body['assignment']))

def repeat(arguments):
    (success, result) = request_repeat(arguments.config_path, arguments.server)

    if (not success):
        print('The autograder could not repeat your last grade for this assignment.')
        print('Message from the autograder: ' + result)
        return 1

    print('The autograder successfully found your last attempt for this assignment.')
    print(result.report())

    return 0

def main(arguments):
    if (arguments.task == TASK_SUBMIT):
        return submit(arguments)
    elif (arguments.task == TASK_REPEAT):
        return repeat(arguments)
    else:
        print("ERROR: unknown task: '%s'." % (arguments.task))
        return 100

def _load_args():
    parser = argparse.ArgumentParser(description = 'Submit a notebook to the autograding server.')

    parser.add_argument('task',
        action = 'store', type = str, default = TASK_SUBMIT,
        choices = TASKS,
        help = 'The task to request from the autograder (default: %(default)s).')

    parser.add_argument('--config', dest = 'config_path',
        action = 'store', type = str, default = DEFAULT_CONFIG_PATH,
        help = 'The JSON config file with your authentication details (default: %(default)s).')

    parser.add_argument('--submission', dest = 'submission_path',
        action = 'store', type = str, default = DEFAULT_SUBMISSION_PATH,
        help = 'The path to your submission (default: %(default)s).')

    parser.add_argument('--server', dest = 'server',
        action = 'store', type = str, default = DEFAULT_AUTOGRADER_URL,
        help = 'The URL of the server to submit to (default: %(default)s).')

    return parser.parse_args()

if (__name__ == '__main__'):
    sys.exit(main(_load_args()))
