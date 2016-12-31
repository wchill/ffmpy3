import errno
import shlex
import asyncio
import subprocess

__version__ = '0.2.3'
__license__ = 'MIT'

# Fork of https://github.com/Ch00k/ffmpy and subject to the terms of the MIT license.
# This is an asynchronous version of the linked project.

"""ffmpy3 is a fork of the `ffmpy <https://github.com/Ch00k/ffmpy>`_ project and subject to the terms of the MIT license.
"""


class FFmpeg(object):
    """Wrapper for various `FFmpeg <https://www.ffmpeg.org/>`_ related applications (ffmpeg,
    ffprobe).
    """

    def __init__(self, executable='ffmpeg', global_options=None, inputs=None, outputs=None):
        """Initialize FFmpeg command line wrapper.

        Compiles FFmpeg command line from passed arguments (executable path, options, inputs and
        outputs). ``inputs`` and ``outputs`` are dictionares containing inputs/outputs as keys and
        their respective options as values. One dictionary value (set of options) must be either a
        single space separated string, or a list or strings without spaces (i.e. each part of the
        option is a separate item of the list, the result of calling ``split()`` on the options
        string). If the value is a list, it cannot be mixed, i.e. cannot contain items with spaces.
        An exception are complex FFmpeg command lines that contain quotes: the quoted part must be
        one string, even if it contains spaces (see *Examples* for more info).
        For more info about FFmpeg command line format see `here
        <https://ffmpeg.org/ffmpeg.html#Synopsis>`_.

        :param str executable: path to ffmpeg executable; by default the ``ffmpeg`` command will be
            searched for in the ``PATH``, but can be overridden with an absolute path to ``ffmpeg``
            executable
        :param iterable global_options: global options passed to ``ffmpeg`` executable (e.g.
            ``-y``, ``-v`` etc.); can be specified either as a list/tuple/set of strings, or one
            space-separated string; by default no global options are passed
        :param dict inputs: a dictionary specifying one or more input arguments as keys with their
            corresponding options (either as a list of strings or a single space separated string) as
            values
        :param dict outputs: a dictionary specifying one or more output arguments as keys with their
            corresponding options (either as a list of strings or a single space separated string) as
            values
        """
        self.executable = executable
        self._cmd = [executable]

        global_options = global_options or []
        if _is_sequence(global_options):
            normalized_global_options = []
            for opt in global_options:
                normalized_global_options += shlex.split(opt)
        else:
            normalized_global_options = shlex.split(global_options)

        self._cmd += normalized_global_options
        self._cmd += _merge_args_opts(inputs, add_input_option=True)
        self._cmd += _merge_args_opts(outputs)

        self.cmd = subprocess.list2cmdline(self._cmd)
        self.process = None

    def __repr__(self):
        return '<{0!r} {1!r}>'.format(self.__class__.__name__, self.cmd)

    def run(self, input_data=None, stdout=None, stderr=None):
        """Execute FFmpeg command line.
        ``input_data`` can contain input for FFmpeg in case ``pipe`` protocol is used for input.
        ``stdout`` and ``stderr`` specify where to redirect the ``stdout`` and ``stderr`` of the
        process. By default no redirection is done, which means all output goes to running shell
        (this mode should normally only be used for debugging purposes). If FFmpeg ``pipe`` protocol
        is used for output, ``stdout`` must be redirected to a pipe by passing `subprocess.PIPE` as
        ``stdout`` argument.
        Returns a 2-tuple containing ``stdout`` and ``stderr`` of the process. If there was no
        redirection or if the output was redirected to e.g. `os.devnull`, the value returned will
        be a tuple of two `None` values, otherwise it will contain the actual ``stdout`` and
        ``stderr`` data returned by ffmpeg process.
        More info about ``pipe`` protocol `here <https://ffmpeg.org/ffmpeg-protocols.html#pipe>`_.
        :param str input_data: input data for FFmpeg to deal with (audio, video etc.) as bytes (e.g.
            the result of reading a file in binary mode)
        :param stdout: redirect FFmpeg ``stdout`` there (default is `None` which means no
            redirection)
        :param stderr: redirect FFmpeg ``stderr`` there (default is `None` which means no
            redirection)
        :return: a 2-tuple containing ``stdout`` and ``stderr`` of the process
        :rtype: tuple
        :raise: `FFRuntimeError` in case FFmpeg command exits with a non-zero code;
            `FFExecutableNotFoundError` in case the executable path passed was not valid
        """
        try:
            self.process = subprocess.Popen(
                self._cmd,
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise FFExecutableNotFoundError("Executable '{0}' not found".format(self.executable))
            else:
                raise

        out = self.process.communicate(input=input_data)
        if self.process.returncode != 0:
            raise FFRuntimeError(self.cmd, self.process.returncode, out[0], out[1])

        return out

    @asyncio.coroutine
    def run_async(self, input_data=None, stdout=None, stderr=None):
        """Asynchronously execute FFmpeg command line.

        ``input_data`` can contain input for FFmpeg in case ``pipe`` protocol is used for input.
        ``stdout`` and ``stderr`` specify where to redirect the ``stdout`` and ``stderr`` of the
        process. By default no redirection is done, which means all output goes to running shell
        (this mode should normally only be used for debugging purposes). If FFmpeg ``pipe`` protocol
        is used for output, ``stdout`` must be redirected to a pipe by passing `subprocess.PIPE` as
        ``stdout`` argument.

        Note that the parent process is responsible for reading any output from stdout/stderr. This
        should be done even if the output will not be used since the process may otherwise deadlock.
        This can be done by awaiting on ``communicate()`` on the returned Process or by manually reading
        from the pipes as necessary.

        Returns a reference to the child process created for use by the parent program.

        More info about ``pipe`` protocol `here <https://ffmpeg.org/ffmpeg-protocols.html#pipe>`_.

        :param str input_data: input data for FFmpeg to deal with (audio, video etc.) as bytes (e.g.
            the result of reading a file in binary mode)
        :param stdout: redirect FFmpeg ``stdout`` there (default is `None` which means no
            redirection)
        :param stderr: redirect FFmpeg ``stderr`` there (default is `None` which means no
            redirection)
        :return: the child process created
        :rtype: asyncio.subprocess.Process
        :raise: `FFExecutableNotFoundError` in case the executable path passed was not valid
        """
        try:
            if input_data:
                stdin = asyncio.subprocess.PIPE
            else:
                stdin = None
            self.process = yield from asyncio.create_subprocess_exec(
                *self._cmd,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise FFExecutableNotFoundError("Executable '{0}' not found".format(self.executable))
            else:
                raise

        if input_data:
            self.process.stdin.write(input_data)

        return self.process

    @asyncio.coroutine
    def wait(self):
        """Asynchronously wait for FFmpeg to complete execution.

        :return: 0 if FFmpeg finished successfully, None if FFmpeg was not started
        :rtype: int
        :raise: `FFRuntimeError` if FFmpeg exited with an error
        """
        if not self.process:
            return None
        exitcode = yield from self.process.wait()
        if exitcode != 0:
            raise FFRuntimeError(self.cmd, exitcode)
        return exitcode


class FFprobe(FFmpeg):
    """Wrapper for `ffprobe <https://www.ffmpeg.org/ffprobe.html>`_."""

    def __init__(self, executable='ffprobe', global_options='', inputs=None):
        """Create an instance of FFprobe.

        Compiles FFprobe command line from passed arguments (executable path, options, inputs).
        FFprobe executable by default is taken from ``PATH`` but can be overridden with an
        absolute path. For more info about FFprobe command line format see
        `here <https://ffmpeg.org/ffprobe.html#Synopsis>`_.

        :param str executable: absolute path to ffprobe executable
        :param iterable global_options: global options passed to ffmpeg executable; can be specified
            either as a list/tuple of strings or a space-separated string
        :param dict inputs: a dictionary specifying one or more inputs as keys with their
            corresponding options as values
        """
        super(FFprobe, self).__init__(
            executable=executable,
            global_options=global_options,
            inputs=inputs
        )


class FFExecutableNotFoundError(Exception):
    """Raise when FFmpeg/FFprobe executable was not found."""


class FFRuntimeError(Exception):
    """Raise when FFmpeg/FFprobe command line execution returns a non-zero exit code.

    The resulting exception object will contain the attributes relates to command line execution:
    ``cmd``, ``exit_code``.
    ``stdout`` and ``stderr`` will also be provided if FFmpeg/FFprobe was executed synchronously.
    """

    def __init__(self, cmd, exit_code, stdout=None, stderr=None):
        self.cmd = cmd
        self.exit_code = exit_code

        message = "`{0}` exited with status {1}\n\nSTDOUT:\n{2}\n\nSTDERR:\n{3}".format(
            self.cmd,
            exit_code,
            (stdout or b'').decode(),
            (stderr or b'').decode()
        )

        super(FFRuntimeError, self).__init__(message)


def _is_sequence(obj):
    """Check if the object is a sequence (list, tuple etc.).

    :param object obj: an object to be checked
    :return: True if the object is iterable but is not a string, False otherwise
    :rtype: bool
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def _merge_args_opts(args_opts_dict, **kwargs):
    """Merge options with their corresponding arguments.

    Iterates over the dictionary holding arguments (keys) and options (values). Merges each
    options string with its corresponding argument.

    :param dict args_opts_dict: a dictionary of arguments and options
    :param dict kwargs: *input_option* - if specified prepends ``-i`` to input argument
    :return: merged list of strings with arguments and their corresponding options
    :rtype: list
    """
    merged = []

    if not args_opts_dict:
        return merged

    for arg, opt in args_opts_dict.items():
        if not _is_sequence(opt):
            opt = shlex.split(opt or '')
        merged += opt

        if not arg:
            continue

        if 'add_input_option' in kwargs:
            merged.append('-i')

        merged.append(arg)

    return merged
