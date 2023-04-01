# UCSC CSE 40

Materials for UCSC's CSE 40 course taught by Dr. Lise Getoor and managed by the [LINQS linqs](https://linqs.org/).
This package is available on PyPi at [ucsc-cse40](https://pypi.org/project/ucsc-cse40/).

### Dependencies

This package is meant to be the sole direct dependency for CSE 40 students.
Instead of specifying each dependency for students, this package defines the necessary dependencies to be installed along with it.
So if you install this package (e.g. via pip), then it will also install all the necessary Python package dependencies for the course.

### Checking Style

This package provides style checking infrastructure using [flake8](https://flake8.pycqa.org).
[PEP8](https://pep8.org/) is generally followed, with a few exceptions.
The exceptions are listed in [cse40.style](https://github.com/ucsc-cse-40/ucsc-cse40/blob/main/cse40/style.py).
For error/violation codes, see [pycodestyle's codes](https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes) and [flake8's codes](https://flake8.pycqa.org/en/latest/user/error-codes.html).

Style can also be checked on the command-line with:
```bash
python -m cse40.style <.py or .ipynb file>
```

### Interacting with the Autograder

All interaction with the autograder is done using the `cse40.autograder` tool included in the `ucsc-cse40` package.
Once the `ucsc-cse40` package is installed on your machine, you can invoke the tool using `python3 -m`.

For example, you can get a help prompt using:
```
python3 -m cse40.autograder --help
```

The tool has options to configure how it runs (as seen in the help prompt),
but as long as you run the tool in your assignment directory (the one that this file lives in)
then all the default options should work just fine.

#### Submitting

To submit your code, you can use the `submit` command:
```
python3 -m cse40.autograder submit
```

If the grading was successful, then you will see output that is very similar to the local grader.
For example, you may see output like:
```
The autograder successfully graded your assignment.
Autograder transcript for project: Hands-On 0: Getting Started.
Grading started at 2023-03-30 17:57 and ended at 2023-03-30 17:57.
Q1: 0 / 100
   NotImplemented returned.
Style: 0 / 0
   Style is clean!

Total: 0 / 100
```

#### Checking Your Last Score

You can ask the autograder to show you your last submission using the `repeat` command:
```
python3 -m cse40.autograder repeat
```

If the lookup was successful, then you will see output that is very similar to when you submitted your code originally.
For example, you may see output like:
```
The autograder successfully found your last attempt for this assignment.
Autograder transcript for project: Hands-On 0: Getting Started.
Grading started at 2023-03-30 17:57 and ended at 2023-03-30 17:57.
Q1: 0 / 100
   NotImplemented returned.
Style: 0 / 0
   Style is clean!

Total: 0 / 100
```

#### Checking Your Score History

To check all your previous scores for this assignment, you can use the `history` command:
```
python3 -m cse40.autograder history
```

This command will return a summary of your past submissions, like:
```
The autograder successfully found your last attempts for this assignment.
Past attempts:
    2023-03-30 17:57 --   0 / 100 (  0.00%)
    2023-03-30 17:59 -- 100 / 100 (100.00%)
```
