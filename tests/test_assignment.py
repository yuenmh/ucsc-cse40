import unittest

import cse40.question
import cse40.assignment

class TestAssignment(unittest.TestCase):
    class Q1(cse40.question.Question):
        def __init__(self):
            super().__init__("Q1", 1)

        def score_question(self, submission):
            result = submission()

            if (result):
                self.full_credit()
            else:
                self.fail()

    def test_base_full_credit(self):
        questions = [
            TestAssignment.Q1(),
        ]

        submission = lambda: True

        assignment = cse40.assignment.Assignment('test_base_full_credit', questions)
        assignment.grade(submission, show_exceptions = True)

        total_score, max_score = assignment.get_score()

        self.assertEqual(total_score, 1)
        self.assertEqual(max_score, 1)

    def test_base_fail(self):
        questions = [
            TestAssignment.Q1(),
        ]

        submission = lambda: False

        assignment = cse40.assignment.Assignment('test_base_fail', questions)
        assignment.grade(submission, show_exceptions = True)

        total_score, max_score = assignment.get_score()

        self.assertEqual(total_score, 0)
        self.assertEqual(max_score, 1)
