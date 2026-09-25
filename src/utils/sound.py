"""Play the apply chime without depending on browser autoplay permissions."""
import ctypes
from ctypes import wintypes
import threading
import uuid

from src.utils.helpers import get_resource_path
from src.utils.logger import log

_play_lock = threading.Lock()


def _play_mp3(path, volume):
    winmm = ctypes.WinDLL('winmm')
    winmm.mciSendStringW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, wintypes.HWND]
    winmm.mciSendStringW.restype = wintypes.DWORD
    winmm.mciGetErrorStringW.argtypes = [wintypes.DWORD, wintypes.LPWSTR, wintypes.UINT]
    winmm.mciGetErrorStringW.restype = wintypes.BOOL

    def command(text):
        error = winmm.mciSendStringW(text, None, 0, None)
        if error:
            message = ctypes.create_unicode_buffer(512)
            winmm.mciGetErrorStringW(error, message, len(message))
            raise RuntimeError(f'Windows audio error {error}: {message.value}')

    alias = 'ffm_chime_' + uuid.uuid4().hex
    command(f'open "{path}" type mpegvideo alias {alias}')
    try:
        command(f'setaudio {alias} volume to {volume * 10}')
        command(f'play {alias} wait')
    finally:
        command(f'close {alias}')


def play_apply_sound(settings):
    if not settings.get('apply_sound_enabled', True):
        return
    volume = max(0, min(100, int(settings.get('apply_sound_volume', 100))))
    if not volume:
        return

    def worker():
        # Avoid overlapping chimes from near-simultaneous apply requests.
        if not _play_lock.acquire(blocking=False):
            return
        try:
            _play_mp3(get_resource_path('src/gui/ui/apply.mp3'), volume)
        except Exception as exc:
            log(f'[!] Apply sound failed: {exc}', (255, 100, 100))
        finally:
            _play_lock.release()

    threading.Thread(target=worker, daemon=True).start()
