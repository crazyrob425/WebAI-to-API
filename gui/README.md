# WebAI-to-API Desktop GUI

A native Windows desktop application built with C++ and Qt6 that provides a graphical interface for the WebAI-to-API backend.

## Features

- **Native Windows GUI** - No terminal window required
- **Server Control** - Start/stop the API server from the GUI
- **System Tray** - Run in background with system tray icon
- **Test Console** - Test API calls directly from the app
- **Settings Panel** - Configure browser, proxy, and model options
- **Live Logs** - View server output in real-time

## Requirements

- Qt6 (with Qt Creator)
- MinGW or MSVC compiler
- Poetry (for Python dependencies)
- Python 3.10+

## Building

### Using Qt Creator

1. Open Qt Creator
2. File → Open File or Project
3. Navigate to `gui/WebAI-to-API.pro`
4. Select your compiler (MinGW or MSVC)
5. Click Configure Project
6. Build → Build All (Ctrl+B)
7. Run (F5)

### Using Command Line

```bash
cd gui
qmake WebAI-to-API.pro
make release
```

## Project Structure

```
gui/
├── WebAI-to-API.pro    # Qt project file
├── main.cpp            # Application entry point
├── mainwindow.h        # Main window header
├── mainwindow.cpp      # Main window implementation
└── README.md           # This file
```

## Usage

1. Ensure Poetry and Python dependencies are installed:
   ```bash
   poetry install
   ```

2. Build and run the GUI application

3. Click "Start Server" to launch the backend

4. Use the "Test Chat" tab to try the API

## Notes

- The GUI expects to find the Python backend in the parent directory's `src/` folder
- Make sure your browser is logged into Gemini for cookie-based authentication
- The server runs on port 6969 by default (configurable)

