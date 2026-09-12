# coding=utf-8
from __future__ import annotations

import threading

import octoprint.plugin


class StayAwakePlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self) -> None:
        self._timer: threading.Timer | None = None
        self._scheduler_lock = threading.Lock()
        self._running = False

    def get_settings_defaults(self):
        return {
            "enabled": False,
            "command": "M105",
            "interval": 30,
            "run_mode": "idle",
        }

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    def on_after_startup(self):
        self._running = True
        self._schedule_next_tick()

    def on_shutdown(self):
        self._running = False
        self._cancel_timer()

    def _cancel_timer(self):
        with self._scheduler_lock:
            timer = self._timer
            self._timer = None

        if timer is not None:
            timer.cancel()

    def _get_interval_seconds(self) -> int:
        raw_interval = self._settings.get(["interval"])

        try:
            interval = int(raw_interval)
        except (TypeError, ValueError):
            interval = 30

        return max(1, interval)

    def _schedule_next_tick(self):
        if not self._running:
            return

        interval = self._get_interval_seconds()
        next_timer = threading.Timer(interval, self._on_timer_tick)
        next_timer.daemon = True

        old_timer = None
        with self._scheduler_lock:
            if not self._running:
                return

            old_timer = self._timer
            self._timer = next_timer

        if old_timer is not None:
            old_timer.cancel()

        with self._scheduler_lock:
            if not self._running or self._timer is not next_timer:
                return

        next_timer.start()

    def _should_send_in_mode(self, run_mode: str) -> bool:
        is_printing_or_paused = self._printer.is_printing() or self._printer.is_paused()

        if run_mode == "printing":
            return is_printing_or_paused
        if run_mode == "always":
            return True

        # Default to idle mode for unknown values.
        return not is_printing_or_paused

    def _on_timer_tick(self):
        try:
            enabled = self._settings.get_boolean(["enabled"])
            command = (self._settings.get(["command"]) or "").strip()
            run_mode = (self._settings.get(["run_mode"]) or "idle").strip().lower()

            if not enabled:
                return

            if not command:
                self._logger.debug("StayAwake tick skipped: command is empty")
                return

            if self._printer is None or not self._printer.is_operational():
                self._logger.debug("StayAwake tick skipped: printer is not operational")
                return

            if not self._should_send_in_mode(run_mode):
                self._logger.debug("StayAwake tick skipped: run mode '%s' conditions not met", run_mode)
                return

            self._printer.commands([command])
            self._logger.debug("StayAwake sent command '%s' in mode '%s'", command, run_mode)
        except Exception:
            self._logger.exception("StayAwake timer tick failed")
        finally:
            self._schedule_next_tick()


__plugin_name__ = "Stay Awake"
__plugin_pythoncompat__ = ">=3.8,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = StayAwakePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {}
