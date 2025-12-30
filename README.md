🏃‍♂️ Velocity Dash
===================

Velocity Dash is a high-octane, minimalist infinite runner built with Python and Pygame. While the mechanics are simple, the focus is on juicy Visual Effects (VFX) and smooth movement physics. Whether you're a developer looking to study Pygame VFX or a player looking for a quick challenge, this project is designed to be lightweight and easy to get running. 🚀

Quick Start
-----------

Don't worry if you've never touched Python before. Follow these steps exactly and you'll be playing in under 2 minutes.

1. Prerequisites
   - Make sure you have Python 3.10+ installed.
     - Windows: Download from https://python.org. Crucial: check the box that says "Add Python to PATH" during installation.
     - macOS / Linux: Usually pre-installed. Check with:
       ```bash
       python3 --version
       ```

2. Setup & Run  
   Open your terminal (or CMD) and run these commands:

   Windows
   ```bash
   # Create and enter a virtual environment
   python -m venv venv
   venv\Scripts\activate

   # Install requirements
   pip install pygame

   # Launch the game
   python main.py
   ```

   macOS / Linux
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install pygame
   python3 main.py
   ```

How to Play 🎮
--------------

Action — Key
- Start Game — ENTER ⏯  
- Move Left / Right — A / D ⬅️➡️  
- Jump / Double Jump — W ⤴️  
- Dash (Fast Move) — SPACE ⚡️  
- Ground Slam — S (while in mid-air) ⤵️  
- Pause / Resume — P ⏸/▶️  
- Exit — ESC ❌

Goal: Keep running, land on platforms, and avoid falling off-screen. Score increases over time.

Customizing the Game 🛠
----------------------

The project is modular. If you want to tweak the gameplay, you don't need to dig through hundreds of lines of code—just open `settings.py`:

- Physics: Adjust `GRAVITY`, `JUMP_POWER`, or `PLAYER_SPEED`.
- Visuals: Change `THEMES` (colors) or `PLAYER_SHAPES`.
- Performance: If the game lags, set `PERFORMANCE_MODE = True` in `main.py` to cap the VFX count.

Building a Windows Standalone (.exe) 📦
-------------------------------------

Want to send the game to a friend who doesn't have Python? You can bundle everything into a folder:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the helper script:
   - Double-click `runner.bat` or run it from CMD:
     ```bash
     runner.bat
     ```

3. Check the `dist/VelocityDash_Final/` (or `dist/DayiRunner_Final/`) folder for your executable.

Troubleshooting 🔧
-----------------

- "No module named pygame": Your virtual environment isn't active. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS / Linux), then `pip install pygame`.
- "Black Screen": This usually happens with certain display scaling or fullscreen settings. Open `main.py` and ensure `pygame.SCALED` is used in the `set_mode` function instead of `FULLSCREEN`, or remove fullscreen flags.
- No Sound / mixer errors: The game includes a silent fallback mode for missing assets, but if you see mixer initialization errors, update audio drivers or try a smaller buffer. Ensure `pygame.mixer.pre_init(...)` runs before `pygame.init()` (the code usually does).

Contributing & License ❤️
-------------------------

- Feel free to fork this, add new obstacles, or improve the VFX.
- License: MIT — free to use, modify, and distribute.
- Assets: If you add custom sprites or audio to the `assets/` folder, the game will automatically detect and use them.

Extras / Tips ✨
---------------

- Lower resolution or set `PERFORMANCE_MODE = True` in `main.py` to improve performance on low-end machines.
- If building with PyInstaller, run `runner.bat` in a terminal to see log output. If antivirus flags the executable, temporarily whitelist the output folder during testing.

---

If you want, I can:
- Add an MIT LICENSE file to the repo. 🧾  
- Create a small placeholder `assets/` pack (one image + one sound) so the game has default visuals and audio. 🖼️🔊  
- Produce a one-line runnable script to auto-create & activate venv, install pygame, and launch the game. ⌨️

Tell me which of the above you'd like next and I will prepare it.
