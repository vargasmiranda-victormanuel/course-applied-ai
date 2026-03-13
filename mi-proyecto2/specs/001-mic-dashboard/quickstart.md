# Quickstart Guide: Mic Dashboard

**Goal**: Get the Mic Dashboard running locally in under 30 seconds.

---

## Prerequisites

- Modern browser (Chrome 60+, Firefox 55+, Safari 11+, Edge 79+)
- Microphone (built-in or USB)
- Python 3.x **OR** Node.js **OR** VS Code with Live Server extension

---

## Option 1: Python (Simplest)

```bash
# Navigate to project directory
cd mi-proyecto2

# Start server (Python 3)
python -m http.server 8000

# Open browser to:
# http://localhost:8000
```

**macOS/Linux Alternative**:
```bash
python3 -m http.server 8000
```

---

## Option 2: Node.js http-server

```bash
# Install http-server globally (one-time)
npm install -g http-server

# Navigate to project directory
cd mi-proyecto2

# Start server
http-server -p 8000

# Open browser to:
# http://localhost:8000
```

---

## Option 3: VS Code Live Server

1. Install "Live Server" extension by Ritwick Dey
2. Right-click `index.html` in VS Code
3. Select "Open with Live Server"
4. Browser opens automatically

---

## Using the Dashboard

1. **Click "Start Mic"** button
2. **Allow microphone access** when browser prompts
3. **Speak or make sounds** near your microphone
4. **Watch the volume indicator** update in real-time (0-100)
5. **Click "Stop"** to release microphone

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Browser not supported" error | Use Chrome, Firefox, Safari, or Edge (modern version) |
| "Must run from server" error | Don't open `file:///...` directly - use a local server (see above) |
| Permission denied | Click camera/mic icon in browser address bar → Allow |
| No volume showing | Check microphone is connected and working |
| Volume very low | Speak louder or adjust system mic sensitivity |

---

## What You're Learning

This dashboard demonstrates:
- ✅ **getUserMedia API**: Requesting microphone access
- ✅ **Web Audio API**: Processing audio in real-time (AudioContext, AnalyserNode)
- ✅ **requestAnimationFrame**: Smooth animation loops
- ✅ **Error Handling**: Permission management and browser compatibility
- ✅ **Privacy**: No recording - only visualization

---

## Next Steps

- **Read the code**: Start with `app.js` - all logic is commented
- **Experiment**: Modify update frequency, visualization scaling, UI styling
- **Extend**: Add frequency visualization, multiple visualizers, effects

---

**Total Time**: < 30 seconds from server start to working visualization! 🎤📊
