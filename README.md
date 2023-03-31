# yaclipy-tools

An extensible, asyncio interface to subprocesses, plus a set of wrappers around common system tools that works well with [yaclipy](https://pypi.org/project/yaclipy)

## Tools

* curl
* docker
* ffmpeg
* firebase
* gcloud
* git
* gpg
* graphviz
* grep
* kubectl
* md5
* nginx
* openssl
* shasum

The set of tools can easily be extended by subclassing SysTool

## ProcTask

This creates an asynchronous connection to a sub-process.  It is based upon loop.subprocess_exec().

>>> await ProcTask('diff', 'README.md', 'README.md')
0

For more complicated interactions, plugins are used.

>>> await ProcTask.using(Lines(1))('ls', '-al')
[...]

The Lines plugin captured stdout (1) and return a list of lines.
If no plugins want to return a value then the default behavior is to return the returncode as seen in the above example.
If multiple plugins want to return a value then they are returned as a tuple:

>>> await ProcTask.using(Lines, Lines(2))('ls', '-al')
([...], [...])

The first value of the tuple contains the lines from stdout AND stderr, whereas the second list only contains stderr lines.

# Echo

The Echo plugin prints to the print_ext Printer().  By setting the context you can create nice, grouped command output.

# Lines

Capture the output and return a list of strings

# OneLine

Capture the output but only return one of the lines

# Input

Send data to stdin of the process

# Log

Capture the output and send it to a file (or other io.Stream)

# Watch

Ask for the output to be captured so that you can use it asynchronously.


## SysTool

SysTool build upon ProcTask by integrating it with yaclipy and adding more user-facing features, such as:

* configurable command location (no more environment variables)
* Tool availability and version check.  
* Helpful info about how to install missing tools.




[![PyPI - Version](https://img.shields.io/pypi/v/yaclipy-tools.svg)](https://pypi.org/project/yaclipy-tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yaclipy-tools.svg)](https://pypi.org/project/yaclipy-tools)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install yaclipy-tools
```

## License

`yaclipy-tools` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
