# Changelog

All notable changes to Podcast Timer will be documented in this file.

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
