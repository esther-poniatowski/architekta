"""
Command-line entry point for the `architekta` package.

Usage
-----
To invoke the package::

    python -m architekta


See Also
--------
architekta.cli: Command-line interface module for the package.
"""
from .cli import app

app()
