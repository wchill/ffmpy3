.. image:: https://img.shields.io/pypi/v/ffmpy3.svg
    :target: https://pypi.python.org/pypi/ffmpy3
    :alt: Latest version

.. image:: https://travis-ci.org/wchill/ffmpy3.svg?branch=master
    :target: https://travis-ci.org/wchill/ffmpy3
    :alt: Travis-CI

.. image:: https://readthedocs.org/projects/ffmpy3/badge/?version=latest
    :target: http://ffmpy3.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


ffmpy3
======
ffmpy3 is a fork of ffmpy, a simplistic `FFmpeg <http://ffmpeg.org/>`_ command line wrapper. ffmpy implements a Pythonic interface for executing FFmpeg via command line and uses Python's `subprocess <https://docs.python.org/3/library/subprocess.html>`_ module for synchronous execution. Asynchronous execution using `yield from` or `await` is also supported using Python's `asyncio.subprocess <https://docs.python.org/3/library/asyncio-subprocess.html>`_ module.

Installation
------------
You guessed it::

  pip install ffmpy3

Quick example
-------------
The following code snippet executes FFmpeg synchronously, taking ``input.mp4`` from the current directory as the input. It remuxes the contents of ``input.mp4`` into a new file called ``output.avi`` which is saved in the current directory.

.. code:: python

  >>> import ffmpy3
  >>> ff = ffmpy3.FFmpeg(
  ...     inputs={'input.mp4': None},
  ...     outputs={'output.avi': None}
  ... )
  >>> ff.run()

The following code snippet does the same thing as above, but executes FFmpeg asynchronously.

.. code:: python

  >>> ff = ffmpy3.FFmpeg(
  ...     inputs={'input.mp4': None},
  ...     outputs={'output.avi': None}
  ... )
  >>> ff.run_async()
  >>> await ff.wait()

Documentation
-------------
http://ffmpy3.readthedocs.io/en/latest

See `Examples <http://ffmpy3.readthedocs.io/en/latest/examples.html>`_ section for usage examples.

License
-------
ffmpy3 is licensed under the terms of the MIT license.
