from xitomatl.pomodoro import Pomodoro, State
from xitomatl.tasks import SHORT_BREAK_COUNT


class Settings:
    def __init__(self, values=None):
        if values is None:
            self.values = {}
        else:
            self.values = values

    def value(self, key, default=None):
        return default

    def beginReadArray(self, _key):
        return 0

    def endArray(self):
        pass

    def fileName(self):
        return "fake.ini"


def test_pomodoro_init():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    assert pomodoro.state == State.Stopped
    assert pomodoro.current_task().name == "focus"
    assert pomodoro.current_task().minutes == 25


def test_pomodoro_next():
    settings = Settings()
    pomodoro = Pomodoro(settings)

    for i in range(SHORT_BREAK_COUNT):
        pomodoro.next()
        assert pomodoro.state == State.Stopped
        assert pomodoro.current_task().name == "break"
        assert pomodoro.current_task().minutes == 5

        pomodoro.next()
        assert pomodoro.state == State.Stopped
        assert pomodoro.current_task().name == "focus"
        assert pomodoro.current_task().minutes == 25

    pomodoro.next()
    assert pomodoro.state == State.Stopped
    assert pomodoro.current_task().name == "break"
    assert pomodoro.current_task().minutes == 30


def test_pomodoro_start():
    settings = Settings()
    pomodoro = Pomodoro(settings)

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
    pomodoro.finish()
    assert pomodoro.current_task_index == 1
    assert pomodoro.state == State.Stopped
    assert pomodoro.current_task().name == "break"
    assert pomodoro.current_task().minutes == 5
