from setuptools import setup
from setuptools.command.test import test as TestCommand  # noqa
from ffmpy3 import __version__


setup(
    name='ffmpy3',
    version=__version__,
    description='A simple asynchronous Python wrapper for ffmpeg',
    long_description=open('README.rst').read(),
    author='Eric Ahn',
    author_email='ericahn3@illinois.edu',
    license='MIT',
    url='https://github.com/wchill/ffmpy3',
    py_modules=['ffmpy3'],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X'
    ],
    keywords='ffmpeg ffprobe wrapper audio video transcoding'
)
