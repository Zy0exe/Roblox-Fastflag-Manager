from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.utils import sound
from src.gui import api as api_module


@pytest.fixture
def immediate_threads(monkeypatch):
    monkeypatch.setattr(sound.threading, 'Thread', lambda target, **kw: SimpleNamespace(start=target))


@pytest.mark.parametrize('enabled,volume,expected', [(False, 100, None), (True, 0, None), (True, 45, 45), (True, 150, 100)])
def test_sound_settings(monkeypatch, immediate_threads, enabled, volume, expected):
    play = MagicMock()
    monkeypatch.setattr(sound, '_play_mp3', play)
    sound.play_apply_sound({'apply_sound_enabled': enabled, 'apply_sound_volume': volume})
    if expected is None:
        play.assert_not_called()
    else:
        assert play.call_args.args[0].endswith('apply.mp3')
        assert play.call_args.args[1] == expected


def test_audio_failure_logged_and_lock_released(monkeypatch, immediate_threads):
    monkeypatch.setattr(sound, '_play_mp3', MagicMock(side_effect=RuntimeError('device failed')))
    logger = MagicMock()
    monkeypatch.setattr(sound, 'log', logger)
    sound.play_apply_sound({})
    assert 'device failed' in logger.call_args.args[0]
    assert not sound._play_lock.locked()


@pytest.mark.parametrize('count,requested,expected', [(1, True, 1), (0, True, 0), (1, False, 0)])
def test_apply_uses_native_sound_without_window(monkeypatch, immediate_threads, count, requested, expected):
    monkeypatch.setattr(api_module, 'log', MagicMock())
    api = api_module.Api.__new__(api_module.Api)
    api.settings = {}
    api._window = None
    api.flag_manager = MagicMock()
    api.flag_manager.apply_flags_hybrid.return_value = count
    api.roblox_manager = MagicMock()
    play = MagicMock()
    monkeypatch.setattr(api_module, 'play_apply_sound', play)
    api.inject(play_sound=requested)
    assert play.call_count == expected
