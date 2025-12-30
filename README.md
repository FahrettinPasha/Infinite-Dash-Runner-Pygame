# Dayi Runner — Professional, Beginner-Friendly Guide 🚀

Welcome. This README is written in a professional style and also explains every step as if you have never used Python or games before. If you are brand new to this, follow the numbered steps exactly and you will be running the game.

Quick summary:
- What this is: a simple infinite-runner game prototype built with Python and Pygame featuring many visual effects (VFX).
- Goal of this README: get you from zero → to playing the game, and give clear pointers for packaging and modifying the project.

---

Table of contents
1. What you need (prerequisites)
2. How to run the game (step-by-step)
3. How to build a Windows executable
4. Controls and gameplay (short)
5. Project structure — what each file does
6. Key settings you may want to change
7. Common problems and their fixes
8. Contributing, license, and next steps

---

1) What you need (prerequisites) ✅

Minimum requirements:
- A computer with Windows, macOS, or Linux.
- Python 3.10 or newer installed.
- Internet to install dependencies (only for first time).

If you do not know how to install Python:
- Windows: download and run the installer from https://python.org. During install check "Add Python to PATH".
- macOS / Linux: use your system package manager or download from https://python.org.

---

2) How to run the game (step-by-step) ▶️

Follow these EXACT commands in the order shown. If you are on Windows, open Command Prompt (press Windows, type "cmd", Enter). On macOS/Linux, open Terminal.

2.A — Create a safe working environment (recommended)
- Type (copy & paste):

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Explanation: this creates an isolated Python environment so dependencies do not conflict with other projects.

2.B — Install the only required library (Pygame)  
After activating the virtual environment run:

Windows / macOS / Linux:
```bash
pip install pygame
```

2.C — Run the game
```bash
python main.py
```

If the game window opens, you're done — congratulations 🎉.

Notes:
- If you see an error "No module named pygame", you missed install or used wrong Python. Re-check that your environment is active and try `pip install pygame` again.
- The game uses the built-in fallback for missing sounds, so it will run even if you don't have `assets/` present.

---

3) How to build a Windows executable (.exe) — easy method 🧩

There is a helper batch script included: `runner.bat`. It runs PyInstaller and copies the assets into the dist folder.

Steps (Windows only):
1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Double-click `runner.bat` in the project folder OR run it from Command Prompt:
```bash
runner.bat
```

3. When complete, open `dist\DayiRunner_Final\` and run the `.exe`.

If you prefer manual control, run:
```bash
python -m PyInstaller --noconsole --onedir --clean \
  --add-data "assets;assets" \
  --hidden-import=pygame \
  --collect-all pygame \
  --name="DayiRunner_Final" main.py
```

Why packaging can fail:
- Missing assets can be handled but PyInstaller needs to be installed and antivirus sometimes blocks created exe. If the exe is not created, inspect PyInstaller output in the terminal for missing modules.

---

4) Controls and gameplay — plain and short 🎮

- Start game: Press ENTER on the start screen.
- Move left / right: A / D
- Jump: W (you can double-jump)
- Dash (fast move): SPACE
- Slam (ground-pound): S while in the air
- Pause / Resume: P
- Restart after Game Over: R
- Quit: ESC

Goal: keep running, avoid falling off platforms. Score increases over time.

---

5) Project structure — file-by-file (very simple) 📂

- main.py — the game loop, input handling, collision logic, and VFX orchestration.
- settings.py — all constants: resolution, colors, physics values, themes, shape options.
- utils.py — helper functions (drawing the player, sound fallback generator, resource path helper).
- vfx.py — visual effects classes (lightning, sparks, shockwaves, trails, etc.).
- animations.py — CharacterAnimator, screen shake, trail effect classes.
- entities.py — game objects: Platform and Star simple classes.
- ui_system.py — in-game UI and menus.
- assets/ — images, sounds, music (not required, but the game will look/sound better with them).
- runner.bat — helper script to build a Windows executable.
- DayiRunner.spec — sample PyInstaller spec.

If you are a complete beginner: think of each file as a room. main.py is the control room. The others are helpers and decorations.

---

6) Key settings you may want to change (safe edits) 🛠

Open settings.py. The most common edits:
- SCREEN_WIDTH, SCREEN_HEIGHT — change window size/resolution.
- FPS — frames per second (60 is fine).
- GRAVITY, JUMP_POWER, PLAYER_SPEED — change how the character moves.
- DASH_SPEED, DASH_DURATION, DASH_COOLDOWN — tune dash behavior.
- THEMES — change colors; each theme is a dictionary.
- PLAYER_SHAPES — change the available shapes (circle, square, triangle, hexagon).

Notes:
- main.py also contains some runtime toggles (PERFORMANCE_MODE, MAX_VFX_COUNT). These control visual complexity for lower-end machines.

---

7) Common problems and how to fix them — plain English 🔧

Problem: Nothing happens when I run `python main.py`.
- Fix: Make sure you are in the project folder. In terminal run `dir` (Windows) or `ls` (macOS/Linux) to see `main.py`. Activate the virtual environment and run python from the same terminal.

Problem: "pygame.error: mixer not initialized" or no sound.
- Fix: Ensure `pygame.mixer.pre_init(44100, -16, 2, 512)` runs before `pygame.init()` (the code already does). If you still have trouble, try rebooting, or run without sound by muting your audio device.

Problem: Window is black or very small.
- Fix: The code uses fullscreen by default. Open main.py and edit the display flags near the top:
  - Remove `pygame.FULLSCREEN` and use simply `pygame.SCALED` or none.

Problem: Packaged exe does not run or antivirus removes it.
- Fix: Check PyInstaller output for errors. Temporarily disable antivirus, or add the exe to exceptions. Make sure you run runner.bat / PyInstaller on the same machine architecture (32-bit vs 64-bit) you intend to run on.

Problem: Performance is low (slow framerate).
- Fixes (in order):
  1) Open main.py and set `PERFORMANCE_MODE = True`.
  2) Lower `MAX_VFX_COUNT` (e.g., 40).
  3) Reduce `stars` count in main.py.
  4) Reduce resolution in settings.py.

---

8) Contributing, license, and next steps ❤️

Contributing:
- Fork the repository and open a Pull Request (PR).
- Keep changes small and well-explained.
- If you add assets, include them under `assets/` and update any code that uses them.

License:
- This repository currently has no license file. I recommend the MIT license for open and permissive reuse.
- If you want, I can generate an MIT LICENSE file for this repo.

Next steps I can help with (tell me which):
- Add an MIT license file.
- Add a minimal placeholder `assets/` pack (images + example sound).
- Create a simple troubleshooting script that checks Python, Pygame, and PyInstaller versions.
- Make the EXE cross-platform instructions for macOS and Linux packaging.

---

Appendix — exact commands summary (copy/paste) ⌨️

Create & activate environment (Windows):
```bash
python -m venv venv
venv\Scripts\activate
pip install pygame
python main.py
```

Create & activate environment (macOS / Linux):
```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
python3 main.py
```

Package with PyInstaller (Windows example):
```bash
pip install pyinstaller
runner.bat
# or manual:
python -m PyInstaller --noconsole --onedir --clean \
  --add-data "assets;assets" \
  --hidden-import=pygame \
  --collect-all pygame \
  --name="DayiRunner_Final" main.py
```

---

If anything above is unclear or you get an error message, copy the exact error text and paste it here. I will give step-by-step fixes targeted to the exact message. If you want, I can also produce an MIT license file and a simple CONTRIBUTING.md next.
