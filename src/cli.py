"""Windows command-line lifecycle control; no network control port or PID files."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import threading
import time


class Events:
    def __init__(self):
        self.dll = ctypes.WinDLL('kernel32', use_last_error=True)
        self.dll.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
        self.dll.CreateEventW.restype = wintypes.HANDLE
        self.dll.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
        self.dll.OpenEventW.restype = wintypes.HANDLE
        self.dll.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.dll.WaitForSingleObject.restype = wintypes.DWORD
        for name in ('SetEvent', 'CloseHandle'):
            getattr(self.dll, name).argtypes = [wintypes.HANDLE]
            getattr(self.dll, name).restype = wintypes.BOOL
        identity = hashlib.sha256(str(Path.home()).lower().encode()).hexdigest()[:24]
        self.prefix = 'Local\\FFM-CLI-' + identity

    def create(self, name):
        handle = self.dll.CreateEventW(None, True, False, self.prefix + name)
        error = ctypes.get_last_error()
        if not handle:
            raise ctypes.WinError(error)
        if error == 183:
            self.close(handle)
            raise RuntimeError('FFM is already running. Use stop before changing modes.')
        return handle

    def open(self, name, access=0x100000):
        handle = self.dll.OpenEventW(access, False, self.prefix + name)
        if not handle and ctypes.get_last_error() != 2:
            raise ctypes.WinError(ctypes.get_last_error())
        return handle

    def close(self, handle):
        self.dll.CloseHandle(handle)

    def signal(self, handle):
        if not self.dll.SetEvent(handle):
            raise ctypes.WinError(ctypes.get_last_error())

    def wait(self, handle, milliseconds):
        result = self.dll.WaitForSingleObject(handle, milliseconds)
        if result == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        return result == 0

    def state(self):
        handle = self.open('-stop')
        if not handle:
            return 'stopped'
        self.close(handle)
        ready = self.open('-ready')
        if not ready:
            return 'starting'
        try:
            return 'running' if self.wait(ready, 0) else 'starting'
        finally:
            self.close(ready)


def run_app(events, background):
    stop = events.create('-stop')
    ready = None
    try:
        ready = events.create('-ready')
        from src.gui.main_window import MainWindow
        app = MainWindow(background=background)
        if app.api._init_error:
            raise RuntimeError(app.api._init_error)

        def loaded():
            events.signal(ready)

        def watch_stop():
            events.wait(stop, 0xFFFFFFFF)
            app.api.exit_app()

        app.window.events.loaded += loaded
        threading.Thread(target=watch_stop, daemon=True).start()
        app.run()
    finally:
        if ready:
            events.close(ready)
        events.close(stop)


def start(events):
    if events.state() != 'stopped':
        print('FFM is already running. Use stop before changing modes.')
        return 0
    root = Path(__file__).resolve().parents[1]
    if getattr(sys, 'frozen', False):
        command = [sys.executable, 'run', '--background']
    else:
        command = [sys.executable, str(root / 'main.pyw'), 'run', '--background']
    log_path = Path.home() / '.FFlagManager' / 'logs' / 'background-startup.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open('a', encoding='utf-8') as log:
        child = subprocess.Popen(command, cwd=root, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=log,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError(f'Background process exited ({child.returncode}). See {log_path}')
        if events.state() == 'running':
            print('FFM is running without a taskbar or tray icon. Use stop to exit.')
            return 0
        time.sleep(0.1)
    raise RuntimeError(f'Startup is still pending. Use status or stop. See {log_path}')


def stop_app(events):
    handle = events.open('-stop', 0x0002)
    if not handle:
        print('FFM is already stopped.')
        return 0
    try:
        events.signal(handle)
    finally:
        events.close(handle)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if events.state() == 'stopped':
            print('FFM stopped.')
            return 0
        time.sleep(0.1)
    raise RuntimeError('FFM has not exited yet. Check the startup log or Task Manager.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='FFM window and background controls (Windows).')
    parser.add_argument('command', nargs='?', default='gui', choices=['gui', 'start', 'stop', 'status', 'run'])
    parser.add_argument('--background', action='store_true', help='With run: hide the window and omit the tray icon')
    args = parser.parse_args(argv)
    if args.background and args.command != 'run':
        parser.error('--background is only valid with run; start always runs in the background')
    if os.name != 'nt':
        parser.error('This application requires Windows')
    try:
        events = Events()
        if args.command == 'start':
            return start(events)
        if args.command == 'stop':
            return stop_app(events)
        if args.command == 'status':
            state = events.state()
            print('FFM: ' + state)
            return 0 if state == 'running' else 1
        run_app(events, args.background)
        return 0
    except Exception as exc:
        print(f'FFM: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
