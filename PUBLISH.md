# Publishing to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `podcast-timer`
3. Description: "Professional dual-timer for podcast recording with visual cues"
4. Choose: Public
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Initialize Git and Push

Open Command Prompt in the `C:\claude\podcast_timer` folder and run:

```bash
git init
git add .
git commit -m "Initial commit: Podcast Timer v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/podcast-timer.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Create a Release (This triggers exe builds!)

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Click "Choose a tag" → Type `v1.0.0` → "Create new tag"
4. Release title: `Podcast Timer v1.0.0`
5. Description:
   ```
   Initial release of Podcast Timer!
   
   Features:
   - Dual timers for episode and speaker management
   - Visual color-coded feedback
   - Audio cues at timing thresholds
   - Customizable themes and settings
   - Pause/Resume functionality
   ```
6. Click "Publish release"

**GitHub Actions will automatically build executables for Windows, macOS, and Linux!**

Check the "Actions" tab to watch the build progress. When complete, the executables will be attached to your release.

## Step 4: Update README

After creating the repo, update the README.md:
- Replace `YOUR_USERNAME` with your GitHub username in the clone URL
- Add a screenshot (optional but recommended)

## Future Updates

To release new versions:

```bash
# Make your changes, then:
git add .
git commit -m "Description of changes"
git push

# Create a new release tag
git tag v1.0.1
git push origin v1.0.1
```

Then create a new release on GitHub using that tag - builds will trigger automatically!

## Taking a Screenshot

1. Run the app at 100% zoom
2. Set timers to something interesting (maybe mid-countdown with yellow/red states)
3. Take a screenshot
4. Save as `screenshot.png` in the project folder
5. Commit and push:
   ```bash
   git add screenshot.png
   git commit -m "Add screenshot"
   git push
   ```
