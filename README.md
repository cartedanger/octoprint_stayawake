# OctoPrint Stay Awake

OctoPrint Stay Awake is a lightweight plugin that periodically sends a configured G-code command while the printer is connected and operational.

It is intended for keepalive-style use cases where you want regular firmware communication under selected conditions.

## Settings

- **Enabled** (`enabled`): turn periodic sending on or off.
- **Command** (`command`): G-code to send (default: `M105`).
- **Interval** (`interval`): send period in seconds (default: `30`, minimum `1`).
- **Run mode** (`run_mode`): one of:
  - `idle`: send only when **not printing** and **not paused**.
  - `printing`: send only when **printing or paused**.
  - `always`: send whenever the printer is operational.

## Behavior details

- The scheduler starts when OctoPrint starts.
- The **first command is sent only after the configured interval elapses**.
- If disabled, command is empty, or printer is not operational, no command is sent.
- Timer reschedules safely even if an exception occurs.
- Timer is canceled cleanly on shutdown.

## Installation

### Option 1: Plugin Manager from URL

In OctoPrint:
1. Go to **Settings → Plugin Manager**.
2. Click **Get More...** and then **... from URL**.
3. Use a tagged release/source archive URL (recommended), for example:
   - `https://github.com/cartedanger/octoprint_stayawake/archive/refs/tags/v0.1.0.zip`
4. Install and restart OctoPrint.

### Option 2: Plugin Manager from local ZIP

1. Download this repository as ZIP from GitHub.
2. In OctoPrint, go to **Settings → Plugin Manager**.
3. Click **... from file** and select the downloaded ZIP.
4. Install and restart OctoPrint.

## Basic usage example

1. Enable the plugin.
2. Set **Command** to `M105`.
3. Set **Interval** to `30`.
4. Select run mode (`idle`, `printing`, or `always`) based on your goal.

## Safety note

Use keepalive behavior carefully. Do not rely on this plugin to bypass critical safety, thermal, or power protections. Ensure heaters and printer safety mechanisms are managed intentionally.
