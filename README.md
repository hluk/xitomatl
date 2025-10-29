Simple **pomodoro** timer app residing in tray.

# Install and Run

There is no need to install the app. Single file executables are provided.

You can grab latest build artifacts from [a successful GitHub action
run](https://github.com/hluk/xitomatl/actions?query=is%3Asuccess).

# Workflow Example

The application runs as **tray icon** and shows current task **progress in
minutes**.

Initial **stopped** state (if autostart is not enabled):
<img src="images/stopped.png" alt="stopped" width="24" height="24"/>

**Focus** task runs after tray icon is **clicked**:
<img src="images/focus25.png" alt="focus 25 minutes remaining" width="24" height="24"/>
…
<img src="images/focus1.png" alt="focus 1 minute remaining" width="24" height="24"/>
<img src="images/focus0.png" alt="focus 0 minutes remaining" width="24" height="24"/>
<img src="images/focus-1.png" alt="focus 1 minute overtime" width="24" height="24"/>
…

**Break** runs after tray icon is clicked again:
<img src="images/break5.png" alt="break 5 minutes remaining" width="24" height="24"/>
…
<img src="images/break1.png" alt="break 1 minute remaining" width="24" height="24"/>
<img src="images/break0.png" alt="break 0 minutes remaining" width="24" height="24"/>
<img src="images/break-1.png" alt="break 1 minute overtime" width="24" height="24"/>
…

Another focus task runs after tray icon is clicked again:
<img src="images/focus25.png" alt="focus 25 minutes remaining" width="24" height="24"/>
…

After few iterations **large break** runs:
<img src="images/break30.png" alt="break 30 minutes remaining" width="24" height="24"/>
…

The tasks, breaks and their meaning can be **fully customized** in the
configuration file.

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

    uv run xitomatl

Install **pre-commit** for local repository clone:

    pre-commit install

Run **all checks**:

    pre-commit run --all-files
    uv run pytest
