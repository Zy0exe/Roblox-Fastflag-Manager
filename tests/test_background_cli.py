import os
import subprocess
import sys
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.cli import Events, main, stop_app


@pytest.fixture
def events():
    if os.name != 'nt':
        pytest.skip('Windows event integration')
    events = Events()
    events.prefix += '-' + uuid.uuid4().hex
    return events


def test_event_lifecycle_and_duplicate_start(events):
    assert events.state() == 'stopped'
    stop = events.create('-stop')
    ready = events.create('-ready')
    try:
        assert events.state() == 'starting'
        with pytest.raises(RuntimeError, match='already running'):
            events.create('-stop')
        events.signal(ready)
        assert events.state() == 'running'
    finally:
        events.close(ready)
        events.close(stop)
    assert events.state() == 'stopped'


def test_stop_across_processes(events):
    script = '''
import sys
from src.cli import Events
events = Events()
events.prefix = sys.argv[1]
stop = events.create('-stop')
ready = events.create('-ready')
events.signal(ready)
print('ready', flush=True)
assert events.wait(stop, 10000)
events.close(ready)
events.close(stop)
'''
    child = subprocess.Popen([sys.executable, '-c', script, events.prefix], stdout=subprocess.PIPE, text=True)
    try:
        assert child.stdout.readline().strip() == 'ready'
        assert events.state() == 'running'
        assert stop_app(events) == 0
        assert child.wait(timeout=5) == 0
        assert events.state() == 'stopped'
        assert stop_app(events) == 0
    finally:
        if child.poll() is None:
            child.kill()
        child.wait()


@pytest.mark.parametrize('background', [False, True])
def test_window_visibility_and_tray(monkeypatch, background):
    from src.gui import main_window
    api = MagicMock(settings={})
    monkeypatch.setattr(main_window, 'Api', lambda **kwargs: api)
    create = MagicMock(return_value=MagicMock())
    monkeypatch.setattr(main_window.webview, 'create_window', create)
    tray = MagicMock()
    monkeypatch.setattr(main_window.MainWindow, '_setup_tray', tray)
    app = main_window.MainWindow(background=background)
    assert create.call_args.kwargs['hidden'] is background
    assert tray.call_count == (0 if background else 1)
    monkeypatch.setattr(main_window, '_install_nav_guard', lambda: None)
    monkeypatch.setattr(main_window.webview, 'start', lambda callback, window, **kw: callback(window))
    app.run()
    assert app.window.resize.call_count == (0 if background else 1)


def test_invalid_background_command():
    with pytest.raises(SystemExit) as exc:
        main(['status', '--background'])
    assert exc.value.code == 2
