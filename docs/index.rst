ffmpy3
======
ffmpy3 is a Python wrapper for `FFmpeg <https://ffmpeg.org>`_, originally forked from the `ffmpy <https://github.com/Ch00k/ffmpy>`_ project. It compiles FFmpeg command line from provided arguments and their respective options and executes it using Python's :mod:`subprocess` .

ffmpy3 resembles the command line approach FFmpeg uses. It can read from an arbitrary number of input "files" (regular files, pipes, network streams, grabbing devices, etc.) and write into arbitrary number of output "files". See FFmpeg `documentation <https://ffmpeg.org/ffmpeg.html#Synopsis>`_ for further details about how FFmpeg command line options and arguments work.

ffmpy3 supports FFmpeg's `pipe <https://ffmpeg.org/ffmpeg-protocols.html#pipe>`_ protocol. This means that it is possible to pass input data to ``stdin`` and get output data from ``stdout``.

At this moment ffmpy3 has wrappers for ``ffmpeg`` and ``ffprobe`` commands, but it should be possible to run other FFmpeg tools with it (e.g. ``ffserver``).

Installation
------------
::

  pip install ffmpy3

Quickstart
----------
::

  >>> import ffmpy3
  >>> ff = ffmpy3.FFmpeg(
  ...     inputs={'input.mp4': None},
  ...     outputs={'output.avi': None}
  ... )
  >>> ff.run()

This takes ``input.mp4`` file in the current directory as the input, changes the video container from MP4 to AVI without changing any other video parameters and creates a new output file ``output.avi`` in the current directory.

Documentation
-------------
.. toctree::
  :maxdepth: 2

  ffmpy3
  examples
