# Changelog

All notable changes to Podcast Timer will be documented in this file.

## [1.2.0] - 2026-03-05

### Added
- **Auto-update check** — on startup, checks GitHub releases API in background; shows non-blocking green banner if a newer version is available; clicking banner opens browser to releases page
- **Version display** — current version shown in Settings panel next to developer credit; if update found, displays new version number as a clickable link
- **Speaker Timer pause button** — dedicated PAUSE/RESUME button on the Speaker Timer zone (left of NEXT/RESET); pausing speaker keeps episode timer running; NEXT/RESET while paused resets and resumes immediately

### Changed
- **Window resize-to-zoom** — resizing the window now scales the UI proportionally; removed zoom slider from Settings
- **Default window size** — launches at 1.4x scale (~784px wide) for better out-of-box readability
- **Timer survives resize** — UI rebuild on resize now preserves running timer state, remaining time, and button states
- **Settings order** — Audio Cues, Always on Top, Theme (top to bottom)
- **Build workflow** — PyInstaller now names macOS and Linux binaries directly (`PodcastTimer-macOS`, `PodcastTimer-Linux`) eliminating the no-extension duplicate asset

### Fixed
- Initial launch rendered at wrong scale until window was manually resized; now defers UI rebuild 50ms until window is fully realized

## [1.0.0] - 2026-02-27

### Initial Release

#### Features
- **Dual Timer System**
  - Episode Timer: Track overall podcast duration
  - Speaker Timer: Manage individual speaker segments
  
- **Visual Feedback**
  - Color-coded backgrounds (green → yellow → red)
  - Status messages at key thresholds
  - Pulsing effects when timers expire
  - Non-blinking colon for better readability

- **Controls**
  - Inline timer editing via pencil icon
  - Pause/Resume functionality
  - NEXT/RESET for speaker rotation
  - Smart button states (disabled when appropriate)
  
- **Settings**
  - Theme selection (Light/Dark/System)
  - Always-on-top option
  - Audio cue toggle
  
- **Audio Cues**
  - Yellow threshold: 660 Hz tone
  - Red threshold: 440 Hz tone
  - Time's up: Double 330 Hz tones

#### Technical
- Single-file Python application
- Built with CustomTkinter for modern UI
- Cross-platform compatibility (Windows, macOS, Linux)
- Settings persistence via JSON
- Optional audio via pygame-ce

---

**Developed by Damon Downing, 2026**

### Initial Release

#### Features
- **Dual Timer System**
  - Episode Timer: Track overall podcast duration
  - Speaker Timer: Manage individual speaker segments
  
- **Visual Feedback**
  - Color-coded backgrounds (green → yellow → red)
  - Status messages at key thresholds
  - Pulsing effects when timers expire
  - Non-blinking colon for better readability
  
- **Episode Timer Messages**
  - 50-55%: "HALF WAY THERE"
  - 75-90%: "START SUMMARIZING"
  - 90-100%: "FINALIZE THE EPISODE"
  - 100%+: "TIME'S UP" with pulsing
  
- **Speaker Timer Messages**
  - 0-75%: "DOING GREAT"
  - 75-90%: "GET TO THE POINT"
  - 90-100%: "WRAP IT UP"
  - 100%+: "TIME'S UP" with pulsing
  
- **Controls**
  - Inline timer editing via pencil icon
  - Pause/Resume functionality
  - NEXT/RESET for speaker rotation
  - Smart button states (disabled when appropriate)
  
- **Settings**
  - Theme selection (Light/Dark/System)
  - Zoom adjustment (85%-200%)
  - Always-on-top option
  - Audio cue toggle
  - Settings disabled during timer operation
  
- **Audio Cues**
  - Yellow threshold: 660 Hz tone
  - Red threshold: 440 Hz tone
  - Time's up: Double 330 Hz tones
  
- **User Experience**
  - Clean, professional interface
  - Consistent button behavior
  - Developer credit in settings
  - Keyboard shortcuts (Enter, Escape, Tab)
  
#### Technical
- Single-file Python application
- Built with CustomTkinter for modern UI
- Cross-platform compatibility (Windows, macOS, Linux)
- Settings persistence via JSON
- Optional audio via pygame-ce

---

**Developed by Damon Downing, 2026**
