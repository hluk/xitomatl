Simple **pomodoro** timer app residing in tray.

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
