import errno
import shlex
import asyncio
import subprocess

__version__ = '0.2.3'
__license__ = 'MIT'

"""
ffmpy3

ffmpy3 is a fork of the `ffmpy <https://github.com/Ch00k/ffmpy>`_ project and subject to the terms of the MIT license.
"""


class FFmpeg(object):
    """Wrapper for various `FFmpeg <https://www.ffmpeg.org/>`_ related applications (ffmpeg,
    ffprobe).

    Compiles FFmpeg command line from passed arguments (executable path, options, inputs and
    outputs).

    ``inputs`` and ``outputs`` are dictionaries containing inputs/outputs as keys and
    their respective options as values.

    One dictionary value (set of options) must be either a
    single space separated string, or a list or strings without spaces (i.e. each part of the
    option is a separate item of the list, the result of calling ``split()`` on the options
    string).

    If the value is a list, it cannot be mixed, i.e. cannot contain items with spaces.
    An exception are complex FFmpeg command lines that contain quotes: the quoted part must be
    one string, even if it contains spaces (see *Examples* for more info).

    Parameters
    -----------
    executable : str
        path to ffmpeg executable; by default the ``ffmpeg`` command will be searched for in the
        ``PATH``, but can be overridden with an absolute path to ``ffmpeg`` executable
    global_options : iterable
        global options passed to ``ffmpeg`` executable (e.g. ``-y``, ``-v`` etc.); can be specified
        either as a list/tuple/set of strings, or one space-separated string; by default no global
        options are passed
    inputs : dict
        a dictionary specifying one or more input arguments as keys with their corresponding options
        (either as a list of strings or a single space separated string) as values
    outputs : dict
        a dictionary specifying one or more output arguments as keys with their corresponding options
        (either as a list of strings or a single space separated string) as values
    """

    def __init__(self, executable='ffmpeg', global_options=None, inputs=None, outputs=None):
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

        ``input_data`` can contain input for FFmpeg in case `pipe <https://ffmpeg.org/ffmpeg-protocols.html#pipe>`_
        protocol is used for input.

        ``stdout`` and ``stderr`` specify where to redirect the ``stdout`` and ``stderr`` of the
        process. By default no redirection is done, which means all output goes to running shell
        (this mode should normally only be used for debugging purposes).

        If FFmpeg ``pipe`` protocol
        is used for output, ``stdout`` must be redirected to a pipe by passing `subprocess.PIPE` as
        ``stdout`` argument.

        Returns a 2-tuple containing ``stdout`` and ``stderr`` of the process. If there was no
        redirection or if the output was redirected to e.g. `os.devnull`, the value returned will
        be a tuple of two `None` values, otherwise it will contain the actual ``stdout`` and
        ``stderr`` data returned by ffmpeg process.

        Parameters
        -----------
        input_data : bytes
            input data for FFmpeg to deal with (audio, video etc.) as bytes (e.g.
            the result of reading a file in binary mode)
        stdout
            Where to redirect FFmpeg ``stdout`` to. Default is `None`, meaning no redirection.
        stderr
            Where to redirect FFmpeg ``stderr`` to. Default is `None`, meaning no redirection.

        Raises
        -------
        FFExecutableNotFoundError
            The executable path passed was not valid.
        FFRuntimeError
            The process exited with an error.

        Returns
        --------
        tuple
            A 2-tuple containing ``stdout`` and ``stderr`` from the process.
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

        ``input_data`` can contain input for FFmpeg in case `pipe <https://ffmpeg.org/ffmpeg-protocols.html#pipe>`_
        
        ``stdout`` and ``stderr`` specify where to redirect the ``stdout`` and ``stderr`` of the
        process. By default no redirection is done, which means all output goes to running shell
        (this mode should normally only be used for debugging purposes).

        If FFmpeg ``pipe`` protocol
        is used for output, ``stdout`` must be redirected to a pipe by passing `subprocess.PIPE` as
        ``stdout`` argument.

        Note that the parent process is responsible for reading any output from stdout/stderr. This
        should be done even if the output will not be used since the process may otherwise deadlock.
        This can be done by awaiting on :meth:`asyncio.subprocess.Process.communicate` on the returned
        :class:`asyncio.subprocess.Process` or by manually reading from the streams as necessary.

        Returns a reference to the child process created for use by the parent program.

        Parameters
        -----------
        input_data : bytes
            input data for FFmpeg to deal with (audio, video etc.) as bytes (e.g.
            the result of reading a file in binary mode)
        stdout
            Where to redirect FFmpeg ``stdout`` to. Default is `None`, meaning no redirection.
        stderr
            Where to redirect FFmpeg ``stderr`` to. Default is `None`, meaning no redirection.

        Raises
        -------
        FFExecutableNotFoundError
            The executable path passed was not valid.

        Returns
        --------
        :class:`asyncio.subprocess.Process`
            The child process created.
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
        """Asynchronously wait for the process to complete execution.

        Raises
        -------
        FFRuntimeError
            The process exited with an error.

        Returns
        --------
        int or None
            0 if the process finished successfully, or None if it has not been started
        """
        if not self.process:
            return None
        exitcode = yield from self.process.wait()
        if exitcode != 0:
            raise FFRuntimeError(self.cmd, exitcode)
        return exitcode


class FFprobe(FFmpeg):
    """Wrapper for `ffprobe <https://www.ffmpeg.org/ffprobe.html>`_.

    Compiles FFprobe command line from passed arguments (executable path, options, inputs).
    FFprobe executable by default is taken from ``PATH`` but can be overridden with an
    absolute path.
    
    Parameters
    -----------
    executable : str
        absolute path to ffprobe executable
    global_options : iterable
        global options passed to ffprobe executable; can be specified either as a list/tuple of
        strings or a space-separated string
    inputs : dict
        a dictionary specifying one or more inputs as keys with their corresponding options as values
    """

    def __init__(self, executable='ffprobe', global_options='', inputs=None):
        super(FFprobe, self).__init__(
            executable=executable,
            global_options=global_options,
            inputs=inputs
        )


class FFExecutableNotFoundError(Exception):
    """Raised when FFmpeg/FFprobe executable was not found."""


class FFRuntimeError(Exception):
    """Raised when FFmpeg/FFprobe command line execution returns a non-zero exit code.

    Attributes
    -----------
    cmd : str
        The command used to launch the executable, with all command line options.
    exit_code : int
        The resulting exit code from the executable.
    stdout : bytes
        The contents of stdout (only if executed synchronously).
    stderr : bytes
        The contents of stderr (only if executed synchronously).
    """

    def __init__(self, cmd, exit_code, stdout=b'', stderr=b''):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

        message = "`{0}` exited with status {1}\n\nSTDOUT:\n{2}\n\nSTDERR:\n{3}".format(
            self.cmd,
            exit_code,
            stdout.decode(),
            stderr.decode()
        )

        super(FFRuntimeError, self).__init__(message)


def _is_sequence(obj):
    """Check if the object is a sequence (list, tuple etc.).

    Parameters
    -----------
    object
        an object to be checked

    Returns
    --------
    bool
        True if the object is iterable but is not a string, False otherwise
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def _merge_args_opts(args_opts_dict, **kwargs):
    """Merge options with their corresponding arguments.

    Iterates over the dictionary holding arguments (keys) and options (values). Merges each
    options string with its corresponding argument.

    Parameters
    -----------
    args_opts_dict : dict
        a dictionary of arguments and options
    kwargs : dict
        *input_option* - if specified prepends ``-i`` to input argument

    Returns
    --------
    list
        a merged list of strings with arguments and their corresponding options
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
