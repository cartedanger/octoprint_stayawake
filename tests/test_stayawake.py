import unittest
from unittest.mock import MagicMock
import sys
import types

if "octoprint" not in sys.modules:
    octoprint_module = types.ModuleType("octoprint")
    plugin_module = types.ModuleType("octoprint.plugin")

    plugin_module.SettingsPlugin = type("SettingsPlugin", (), {})
    plugin_module.StartupPlugin = type("StartupPlugin", (), {})
    plugin_module.ShutdownPlugin = type("ShutdownPlugin", (), {})
    plugin_module.TemplatePlugin = type("TemplatePlugin", (), {})
    plugin_module.AssetPlugin = type("AssetPlugin", (), {})
    plugin_module.SimpleApiPlugin = type("SimpleApiPlugin", (), {})

    octoprint_module.plugin = plugin_module
    sys.modules["octoprint"] = octoprint_module
    sys.modules["octoprint.plugin"] = plugin_module

if "flask" not in sys.modules:
    flask_module = types.ModuleType("flask")

    def _jsonify(**kwargs):
        return kwargs

    flask_module.jsonify = _jsonify
    sys.modules["flask"] = flask_module

from octoprint_stayawake import StayAwakePlugin


class StayAwakePluginTests(unittest.TestCase):
    def _plugin(self):
        plugin = StayAwakePlugin()
        plugin._settings = MagicMock()
        plugin._printer = MagicMock()
        plugin._logger = MagicMock()
        plugin._schedule_next_tick = MagicMock()
        return plugin

    def test_interval_defaults_to_minimum_one(self):
        plugin = self._plugin()
        plugin._settings.get.return_value = 0

        self.assertEqual(plugin._get_interval_seconds(), 1)

    def test_interval_invalid_falls_back_to_default(self):
        plugin = self._plugin()
        plugin._settings.get.return_value = "abc"

        self.assertEqual(plugin._get_interval_seconds(), 30)

    def test_tick_skips_when_disabled(self):
        plugin = self._plugin()
        plugin._settings.get_boolean.return_value = False

        plugin._on_timer_tick()

        plugin._printer.commands.assert_not_called()
        plugin._schedule_next_tick.assert_called_once()

    def test_tick_sends_when_idle_mode_and_printer_idle(self):
        plugin = self._plugin()
        plugin._settings.get_boolean.return_value = True
        plugin._settings.get.side_effect = lambda keys: {
            ("command",): "M105",
            ("run_mode",): "idle",
        }.get(tuple(keys))
        plugin._printer.is_operational.return_value = True
        plugin._printer.is_printing.return_value = False
        plugin._printer.is_paused.return_value = False

        plugin._on_timer_tick()

        plugin._printer.commands.assert_called_once_with(["M105"])
        plugin._schedule_next_tick.assert_called_once()

    def test_tick_skips_idle_mode_while_printing(self):
        plugin = self._plugin()
        plugin._settings.get_boolean.return_value = True
        plugin._settings.get.side_effect = lambda keys: {
            ("command",): "M105",
            ("run_mode",): "idle",
        }.get(tuple(keys))
        plugin._printer.is_operational.return_value = True
        plugin._printer.is_printing.return_value = True
        plugin._printer.is_paused.return_value = False

        plugin._on_timer_tick()

        plugin._printer.commands.assert_not_called()
        plugin._schedule_next_tick.assert_called_once()

    def test_send_now_uses_configured_command_when_operational(self):
        plugin = self._plugin()
        plugin._settings.get.side_effect = lambda keys: {
            ("command",): "M110",
        }.get(tuple(keys))
        plugin._printer.is_operational.return_value = True

        sent, error = plugin._send_command_now()

        self.assertTrue(sent)
        self.assertIsNone(error)
        plugin._printer.commands.assert_called_once_with(["M110"])


if __name__ == "__main__":
    unittest.main()
