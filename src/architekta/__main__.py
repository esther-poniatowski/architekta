"""
Entry point for the `architekta` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m architekta


See Also
--------
architekta.cli: Module implementing the application's command-line interface.
"""

from .cli import app

app()
