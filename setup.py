"""
avoviirscollector -- scripts to retrieve viirs data at AVO

"""

from setuptools import setup, find_packages
from avoviirscollector import __version__

DOCSTRING = __doc__.split("\n")

setup(
    name="avoviirscollector",
    version=__version__,
    author="Tom Parker",
    author_email="tparker@usgs.gov",
    description=(DOCSTRING[1]),
    license="CC0",
    url="http://github.com/tparker-usgs/avoviirscollector",
    packages=find_packages(),
    long_description="\n".join(DOCSTRING[3:]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        "pycurl",
        "tomputils>=1.12.16",
        "multiprocessing_logging",
        "h5py",
        "single",
        "boto3",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    scripts=["bin/reprocess"],
    entry_points={
        "console_scripts": [
            "mirror_gina = avoviirscollector.mirror_gina:main",
            "task_broker = avoviirscollector.task_broker:main",
            "msg_publisher = avoviirscollector.msg_publisher:main",
        ]
    },
)
