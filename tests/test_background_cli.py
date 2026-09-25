import os
import subprocess
import sys
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.cli import Events, main, stop_app, request_apply


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


def test_apply_when_stopped(events):
    with pytest.raises(RuntimeError, match='not ready'):
        request_apply(events)


def test_apply_old_running_instance(events):
    stop = events.create('-stop')
    ready = events.create('-ready')
    try:
        events.signal(ready)
        with pytest.raises(RuntimeError, match='ffm stop'):
            request_apply(events)
    finally:
        events.close(ready)
        events.close(stop)


def test_apply_event_resets_after_one_request(events):
    handle = events.create('-apply', manual_reset=False)
    try:
        events.signal(handle)
        assert events.wait(handle, 0)
        assert not events.wait(handle, 0)
    finally:
        events.close(handle)


def test_apply_dispatch_across_processes(events):
    script = '''
import sys, threading, time
from src.cli import Events, watch_apply
events = Events()
events.prefix = sys.argv[1]
stop = events.create('-stop')
ready = events.create('-ready')
apply = events.create('-apply', manual_reset=False)
shutdown = threading.Event()
class Api:
    def inject_user(self):
        print('applied', flush=True)
worker = threading.Thread(target=watch_apply, args=(events, apply, Api(), shutdown))
worker.start()
events.signal(ready)
print('ready', flush=True)
events.wait(stop, 10000)
shutdown.set()
worker.join()
for handle in (apply, ready, stop):
    events.close(handle)
'''
    child = subprocess.Popen([sys.executable, '-c', script, events.prefix], stdout=subprocess.PIPE, text=True)
    try:
        assert child.stdout.readline().strip() == 'ready'
        for _ in range(2):
            assert request_apply(events) == 0
            assert child.stdout.readline().strip() == 'applied'
        assert stop_app(events) == 0
        assert child.wait(timeout=5) == 0
        assert child.stdout.read() == ''  # no repeated apply from a stuck event
    finally:
        if child.poll() is None:
            child.kill()
        child.wait()
