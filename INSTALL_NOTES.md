# Installation Notes

## Qt Platform Plugin Error

If you see an error like:
```
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
```

This means the required X11/XCB system libraries are missing.

### Solution (Ubuntu/Debian)

Run this command to install the required dependencies:

```bash
sudo apt-get update && sudo apt-get install -y libxcb-cursor0
```

### Alternative: Install all Qt5/Qt6 runtime dependencies

If you continue having issues, install a broader set of dependencies:

```bash
sudo apt-get update && sudo apt-get install -y \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-xtest0 \
    libxcb-shape0 \
    libxkbcommon0 \
    libgl1-mesa-glx \
    libdbus-1-3
```

## ROCm Setup

If you plan to use GPU acceleration with ROCm:

```bash
# Verify ROCm is installed
ls /opt/rocm/bin

# Check ROCm version
rocm-smi --version
```

## Running the Application

After installing system dependencies:

```bash
cd /home/dev/opencodeprojects/pixelsmart
bash .venv/activate.sh
python3 src/pixelsmart/main.py
```
