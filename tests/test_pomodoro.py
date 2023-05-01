# SPDX-License-Identifier: LGPL-2.0-or-later
from contextlib import contextmanager
from copy import copy
from unittest.mock import Mock, call, patch

from xitomatl.pomodoro import SHORT_BREAK_COUNT, Pomodoro, State


class Settings(Mock):
    def __init__(self, **kwargs):
        super().__init__()
        self.values = kwargs

    def value(self, key, default=None):
        return self.values.get(key, default)

    def childKeys(self):
        return []


@contextmanager
def mock_commands_run(pomodoro):
    for i, task in enumerate(pomodoro.tasks):
        task = copy(task)
        pomodoro.tasks[i] = task
        task.command_start = f"start{i}"
        task.command_stop = f"stop{i}"
        task.command_finish = f"finish{i}"

    with patch("xitomatl.pomodoro.run") as run:
        run2 = Mock()
        run.side_effect = lambda x, **_kw: run2(x)
        yield run2


def test_pomodoro_init():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    assert pomodoro.state == State.Running
    assert pomodoro.current_task().name == "focus"
    assert pomodoro.current_task().minutes == 25


def test_pomodoro_next():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    for i in range(SHORT_BREAK_COUNT):
        pomodoro.next()
        assert pomodoro.state == State.Running
        assert pomodoro.current_task().name == "break"
        assert pomodoro.current_task().minutes == 5

        pomodoro.next()
        assert pomodoro.state == State.Running
        assert pomodoro.current_task().name == "focus"
        assert pomodoro.current_task().minutes == 25

    pomodoro.next()
    assert pomodoro.state == State.Running
    assert pomodoro.current_task().name == "break"
    assert pomodoro.current_task().minutes == 30


def test_pomodoro_start():
    settings = Settings(autostart="0")
    pomodoro = Pomodoro(settings)

    assert pomodoro.state == State.Stopped
    pomodoro.start()
    assert pomodoro.state == State.Running
    assert pomodoro.current_task().name == "focus"
    assert pomodoro.current_task().minutes == 25


def test_pomodoro_start_next():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    pomodoro.start()
    pomodoro.next()
    assert pomodoro.state == State.Running
    assert pomodoro.current_task().name == "break"
    assert pomodoro.current_task().minutes == 5


def test_pomodoro_stop():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    pomodoro.start()
    pomodoro.next()
    pomodoro.stop()
    assert pomodoro.current_task_index == 0
    assert pomodoro.state == State.Stopped
    assert pomodoro.current_task().name == "focus"
    assert pomodoro.current_task().minutes == 25


def test_pomodoro_finish():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    pomodoro.start()
    assert pomodoro.finished is False
    pomodoro.finish()
    assert pomodoro.finished is True
    pomodoro.next()
    assert pomodoro.finished is False


def test_pomodoro_finish_after_timeout():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    pomodoro.tasks[0].minutes = 0
    pomodoro.start()
    assert pomodoro.finished is True


def test_pomodoro_command_start():
    settings = Settings(autostart="0")
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.start()
        run.assert_called_once_with(["start0"])


def test_pomodoro_command_start_on_restarted():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.start()
        assert run.call_args_list == [call(["stop0"]), call(["start0"])]


def test_pomodoro_command_stop():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.stop()
        run.assert_called_once_with(["stop0"])


def test_pomodoro_command_stop_not_called_if_not_running():
    settings = Settings(autostart="0")
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.stop()
        run.assert_not_called()


def test_pomodoro_command_stop_start_on_next():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.next()
        assert run.call_args_list == [call(["stop0"]), call(["start1"])]


def test_pomodoro_command_not_called_on_next_if_not_running():
    settings = Settings(autostart="0")
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.next()
        run.assert_not_called()


def test_pomodoro_command_finish():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.finish()
        run.assert_called_once_with(["finish0"])


def test_pomodoro_command_finish_on_timeout():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.tasks[0].minutes = 0
        pomodoro.on_timeout()
        run.assert_called_once_with(["finish0"])


def test_pomodoro_command_execute_multiple():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    with mock_commands_run(pomodoro) as run:
        pomodoro.tasks[
            0
        ].command_stop = """
            stop0.1
            stop0.2
        """
        pomodoro.stop()
        assert run.call_args_list == [call(["stop0.1"]), call(["stop0.2"])]
