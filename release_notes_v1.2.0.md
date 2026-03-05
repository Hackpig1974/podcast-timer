## What's New in v1.2.0

### ✨ New Features

**Speaker Timer Pause**
The Speaker Timer now has its own dedicated PAUSE / RESUME button. Pause a speaker's clock mid-segment without touching the episode timer — useful for breaks, intros, or off-topic tangents. Hitting NEXT / RESET while paused resets the speaker timer and resumes immediately.

**Resize-to-Zoom**
Drag any edge of the window and the entire UI scales with it — fonts, buttons, timers, progress bars, all of it. No more zoom slider in Settings; just make the window the size you want.

**Auto-Update Check**
On startup the app silently checks the GitHub releases API. If a newer version is available, a non-blocking green banner appears below the title bar. Click the banner to open the releases page in your browser, or dismiss it with ✕. The current version is also shown in the Settings panel.

---

### 🐛 Bug Fixes

- Fixed a bug where resizing the window while a timer was running would reset both timers back to their starting values. Running timers now survive a resize with all state intact.
- Fixed initial launch rendering at a tiny scale until the window was manually resized. The UI now waits for the window to fully render before building at the correct scale.

---

### ⚙️ Changes

- Default launch size increased to 1.4x (~784px wide) for better out-of-box readability
- Settings panel option order changed to: Audio Cues → Always on Top → Theme
- Build pipeline updated: macOS and Linux binaries are now named directly by PyInstaller, eliminating the duplicate no-extension asset that appeared in previous releases

---

### 📦 Downloads

| Platform | File |
|----------|------|
| Windows | `PodcastTimer.exe` |
| macOS | `PodcastTimer-macOS` |
| Linux | `PodcastTimer-Linux` |

For macOS and Linux, mark the file executable before running:
```bash
chmod +x PodcastTimer-macOS   # or PodcastTimer-Linux
./PodcastTimer-macOS
```

---

*Developed by Damon Downing, 2026*
