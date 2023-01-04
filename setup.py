import setuptools

setuptools.setup(
    name = 'ucsc-cse40',

    version = '0.1.0',

    description = "Dependencies for UCSC's CSE 40: Machine Learning Basics: Data Analysis and Empirical Methods",
    keywords = 'course material',

    maintainer_email = 'eaugusti@ucsc.edu',
    maintainer = 'Eriq Augustine',

    # The project's main homepage.
    url = 'linqs.org',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.7',
    ],

    packages = setuptools.find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
    ],

    python_requires = '>=3.7'
)
