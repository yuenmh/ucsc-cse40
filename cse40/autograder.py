"""
An interface for interacting with the autograder (submitting assignments, querying scores, etc.).
"""

import argparse
import datetime
import json
import sys
import urllib.request

import cse40.assignment
import cse40.code

ENCODING = 'utf-8'
DEFAULT_CONFIG_PATH = 'config.json'
DEFAULT_SUBMISSION_PATH = 'assignment.ipynb'
DEFAULT_AUTOGRADER_URL = 'http://sozopol.soe.ucsc.edu:12345'

TASK_HISTORY = 'history'
TASK_REPEAT = 'repeat'
TASK_SUBMIT = 'submit'
TASKS = [TASK_HISTORY, TASK_REPEAT, TASK_SUBMIT]

DATETIME_FORMAT = '%Y-%m-%d %H:%M'

def request_history(config_path = DEFAULT_CONFIG_PATH, autograde_url = DEFAULT_AUTOGRADER_URL):
    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = TASK_HISTORY

    body, message = _send_request(config, autograde_url)
    if (body is None):
        return (False, message)

    return (True, body['history'])

def request_repeat(config_path = DEFAULT_CONFIG_PATH, autograde_url = DEFAULT_AUTOGRADER_URL):
    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = TASK_REPEAT

    body, message = _send_request(config, autograde_url)
    if (body is None):
        return (False, message)

    return (True, cse40.assignment.Assignment.from_dict(body['assignment']))

def request_submit(config_path = DEFAULT_CONFIG_PATH, submission_path = DEFAULT_SUBMISSION_PATH,
        autograde_url = DEFAULT_AUTOGRADER_URL):
    source_code = cse40.code.extract_code(submission_path)

    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = TASK_SUBMIT
    config['code'] = source_code

    body, message = _send_request(config, autograde_url)
    if (body is None):
        return (False, message)

    return (True, cse40.assignment.Assignment.from_dict(body['assignment']))

def _history(arguments):
    (success, result) = request_history(arguments.config_path, arguments.server)

    if (not success):
        print('The autograder could not compile a history of your past grades for this assignment.')
        print('Message from the autograder: ' + result)
        return 1

    print('The autograder successfully found your last attempts for this assignment.')
    print('Past attempts:')

    for row in result:
        timestamp = datetime.datetime.fromtimestamp(int(row['id'])).strftime(DATETIME_FORMAT)
        score, max_score = row['score']
        percent_score = (100.0 * score / max_score)
        print("    %s -- %3d / %3d (%6.2f%%)" % (timestamp, score, max_score, percent_score))

    return 0

def _repeat(arguments):
    (success, result) = request_repeat(arguments.config_path, arguments.server)

    if (not success):
        print('The autograder could not repeat your last grade for this assignment.')
        print('Message from the autograder: ' + result)
        return 1

    print('The autograder successfully found your last attempt for this assignment.')
    print(result.report())

    return 0

def _submit(arguments):
    (success, result) = request_submit(arguments.config_path, arguments.submission_path,
            arguments.server)

    if (not success):
        print('The autograder failed to grade your assignment.')
        print('Message from the autograder: ' + result)
        return 1

    print('The autograder successfully graded your assignment.')
    print(result.report())

    return 0

def _send_request(config, autograde_url):
    payload = bytes(json.dumps(config), ENCODING)
    raw_response = urllib.request.urlopen(autograde_url, data = payload)

    status = raw_response.status
    if (status != 200):
        return None, "Got a failure status from the autograding server: %s." % (status)

    body = json.loads(raw_response.read().decode(encoding = ENCODING))

    if (body['status'] != 'success'):
        return (None, body['message'])

    return body, None

def main(arguments):
    if (arguments.task == TASK_HISTORY):
        return _history(arguments)
    elif (arguments.task == TASK_REPEAT):
        return _repeat(arguments)
    elif (arguments.task == TASK_SUBMIT):
        return _submit(arguments)
    else:
        print("ERROR: unknown task: '%s'." % (arguments.task))
        return 100

def _load_args():
    parser = argparse.ArgumentParser(description = 'Submit a notebook to the autograding server.')

    parser.add_argument('task',
        action = 'store', type = str, choices = TASKS,
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
