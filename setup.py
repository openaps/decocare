#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import platform

from setuptools import find_packages, setup

import decocare


def readme():
    with open("README.markdown") as f:
        return f.read()


setup(
    name="decocare",
    version="0.1.0",  # http://semver.org/
    description="Audit, inspect, and command MM insulin pumps.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Ben West",
    author_email="bewest+insulaudit@gmail.com",
    url="https://github.com/openaps/decocare",
    # namespace_packages = ['insulaudit'],
    packages=find_packages(),
    install_requires=["pyserial", "python-dateutil", "argcomplete"],
    scripts=[
        "bin/mm-press-key.py",
        "bin/mm-send-comm.py",
        "bin/mm-set-suspend.py",
        "bin/mm-temp-basals.py",
        "bin/mm-decode-history-page.py",
        "bin/mm-latest.py",
        "bin/mm-bolus.py",
        "bin/mm-set-rtc.py",
        "bin/mm-pretty-csv",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    package_data={
        "decocare": ["etc/*", "*.rules"],
        # 'decocare.etc': ['*.rules' ],
    },
    data_files=[
        # commenting out for readthedocs and virtualenv users.
        # ('/etc/udev/rules.d', ['decocare/etc/80-medtronic-carelink.rules'] )
    ],
    zip_safe=False,
)

#####
# EOF
