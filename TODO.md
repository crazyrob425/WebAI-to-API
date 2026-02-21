# TODO: WebAI-to-API GUI - C++ Qt Version

## Task
Create a native Windows GUI application using C++ and Qt that wraps the existing WebAI-to-API backend.

## Features
1. **Native Windows GUI** - No terminal window required for end users
2. **Hidden Backend** - Python server runs invisibly in background
3. **Browser Automation** - Automatically handles browser login for LLMs (headless)
4. **System Tray** - App runs in system tray with menu options
5. **Status Dashboard** - Show connection status, available models, etc.

## Tech Stack
- **Language**: C++
- **Framework**: Qt6
- **Backend**: Python (embedded)
- **Browser Automation**: Playwright/Selenium

## Steps

### Phase 1: Project Setup
- [x] Create Qt project structure (.pro file)
- [x] Set up main.cpp with Qt application
- [x] Configure Qt Creator project
- [ ] Test basic window creation (build in Qt Creator)

### Phase 2: Core GUI
- [ ] Main window with modern UI
- [ ] System tray integration
- [ ] Status indicators
- [ ] Configuration panel

### Phase 3: Backend Integration
- [ ] Embed Python interpreter
- [ ] Auto-start Python server
- [ ] Handle server startup/shutdown
- [ ] IPC between Qt and Python

### Phase 4: Browser Automation
- [ ] Headless browser login for Gemini
- [ ] Cookie extraction
- [ ] Session management

### Phase 5: Build
- [ ] Compile release build
- [ ] Create installer
- [ ] Test on clean system

