Simple **pomodoro** timer app residing in tray.

The application runs as tray icon and shows current task progress in minutes.

# Install and Run

There is no need to install the app. Single file executables are provided.

You can grab latest build artifacts from [a successful GitHub action
run](https://github.com/hluk/xitomatl/actions?query=is%3Asuccess).

# Controls

The behavior may depend on the desktop environment.

* Left mouse button click - Starts next task (the first one if stopped)
* Right mouse button click - Opens menu
* Middle click - Stops and resets progress

# Configuration File

The configuration file contains general settings and task definitions.

The default configuration file location:

* Linux and macOS - `~/.config/xitomatl/xitomatl.ini`
* Windows - `%APPDATA%\copyq`

See [xitomatl.ini](xitomatl.ini) for the default configuration.

# Development

**Qt 6** libraries must be installed on the system.

Clone repository and **start** the app with:

    poetry install
    poetry run xitomatl

Install **pre-commit** for local repository clone:

    pre-commit install

Run **all checks**:

    pre-commit run --all-files
    poetry run pytest
