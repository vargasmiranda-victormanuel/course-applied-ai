# Data Model: Mic Dashboard

**Feature**: 001-mic-dashboard  
**Created**: 2026-02-19  
**Purpose**: Define key entities and their relationships for microphone visualization

## Overview

The Mic Dashboard is a browser-only application with no persistent data storage. All entities are runtime objects managed by the browser's Web Audio API and DOM. This document describes the conceptual data model and state management.

---

## Core Entities

### 1. AudioStream

**Description**: Represents the live microphone input obtained via getUserMedia API.

**Type**: `MediaStream` (browser native object)

**Attributes**:
- `id` (string): Unique identifier for the stream
- `active` (boolean): Whether the stream is currently active
- `tracks` (MediaStreamTrack[]): Array of audio tracks (typically one for microphone)

**Lifecycle**:
- **Created**: When user grants microphone permission via `navigator.mediaDevices.getUserMedia()`
- **Updated**: Continuously receives audio data while active
- **Destroyed**: When `track.stop()` is called on all tracks

**State Transitions**:
```
[Not Started] → [Permission Requested] → [Active] → [Stopped]
                        ↓
                  [Permission Denied]
```

**Relationships**:
- Connected to `AudioContext` via `createMediaStreamSource()`
- Source of audio data for `AnalyserNode`

**Validation Rules**:
- Must have at least one active audio track
- Cannot be reused after tracks are stopped (must request new stream)

---

### 2. AudioContext

**Description**: Web Audio API context that manages audio processing graph and timing.

**Type**: `AudioContext` or `webkitAudioContext` (browser native object)

**Attributes**:
- `state` (string): "suspended", "running", or "closed"
- `sampleRate` (number): Audio sampling rate (typically 44100Hz or 48000Hz)
- `currentTime` (number): Current time position in the audio graph

**Lifecycle**:
- **Created**: When microphone starts (via `new AudioContext()`)
- **Running**: Processes audio while microphone is active
- **Closed**: When microphone stops (via `audioContext.close()`)

**State Transitions**:
```
[Not Created] → [Created/Suspended] → [Running] → [Closed]
                       ↓
                  [Resumed if needed]
```

**Best Practices**:
- Create only one AudioContext instance at a time
- Always close when done to release hardware resources
- Check `state` before performing operations

---

### 3. AnalyserNode

**Description**: Audio processing node that provides real-time frequency and time-domain analysis.

**Type**: `AnalyserNode` (browser native object)

**Attributes**:
- `fftSize` (number): Fast Fourier Transform size (2048 recommended)
- `frequencyBinCount` (number): Half of fftSize (1024 for fftSize=2048)
- `smoothingTimeConstant` (number): 0.0 to 1.0, controls temporal smoothing (0.8 recommended)
- `minDecibels` (number): Minimum power value for scaling (-100 default)
- `maxDecibels` (number): Maximum power value for scaling (-30 default)

**Configuration** (set at creation):
```javascript
analyser.fftSize = 2048;
analyser.smoothingTimeConstant = 0.8;
```

**Methods**:
- `getByteTimeDomainData(Uint8Array)`: Fills array with time-domain (waveform) data 0-255
- `getByteFrequencyData(Uint8Array)`: Fills array with frequency-domain data 0-255

**Relationships**:
- Receives input from `MediaStreamSource` (created from `AudioStream`)
- Provides data for `VolumeLevel` calculation
- Part of `AudioContext` graph

---

### 4. VolumeLevel

**Description**: Calculated numeric representation of current audio amplitude.

**Type**: Application-defined (computed value)

**Attributes**:
- `value` (number): Volume level from 0 to 100
- `timestamp` (number): When this value was calculated (from requestAnimationFrame)
- `rawData` (Uint8Array): Time-domain waveform samples (128 centered around silence)

**Calculation Algorithm**:
```
1. Get time-domain data from AnalyserNode
2. Normalize values: (sample - 128) / 128  // Center around 0
3. Calculate RMS: sqrt(sum(normalized²) / sampleCount)
4. Scale to 0-100: min(100, floor(rms * 100 * 3))
```

**Update Frequency**: 8-12 times per second (100ms interval)

**Validation Rules**:
- Value must be between 0 and 100 (inclusive)
- Must cap at 100 even if calculation exceeds it

**Relationships**:
- Derived from `AnalyserNode` data
- Drives `UIState` updates

---

### 5. UIState

**Description**: Current state of the user interface and application.

**Type**: Application-defined (JavaScript object)

**Attributes**:
```javascript
{
  microphoneStatus: 'off' | 'requesting' | 'on' | 'error',
  volumeValue: number,        // 0-100
  errorMessage: string | null,
  lastUpdateTime: number,     // Timestamp of last update
  animationId: number | null  // requestAnimationFrame ID
}
```

**State Transitions**:
```
[off] → [requesting] → [on] → [off]
           ↓
        [error]
```

**Validation Rules**:
- `microphoneStatus` must be one of the four allowed values
- `volumeValue` must be 0-100
- `errorMessage` is non-null only when status is 'error'
- `animationId` is non-null only when status is 'on'

**Relationships**:
- Updated by volume calculations from `VolumeLevel`
- Drives DOM rendering (numeric display, progress bar, status text)

---

## DOM Elements (UI Components)

### MicrophoneControls

**Elements**:
- `#startButton`: Button to request microphone access
- `#stopButton`: Button to stop microphone and release resources

**State Binding**:
- Buttons enabled/disabled based on `UIState.microphoneStatus`
- Show/hide based on current state

### VolumeDisplay

**Elements**:
- `#volumeValue`: Text element showing numeric volume (0-100)
- `#volumeBar`: Visual progress bar element
- `#volumeBarFill`: Inner element showing fill percentage

**State Binding**:
- Text content driven by `UIState.volumeValue`
- Progress bar width/transform driven by `UIState.volumeValue`

**Update Rate**: Numeric updates at 10Hz, visual bar animates smoothly via CSS transitions

### StatusIndicator

**Elements**:
- `#micStatus`: Text element showing "Mic OFF" or "Mic ON"
- CSS classes for styling (`.mic-on`, `.mic-off`, `.mic-error`)

**State Binding**:
- Text and class driven by `UIState.microphoneStatus`

### ErrorDisplay

**Elements**:
- `#errorContainer`: Container for error messages
- `#errorMessage`: Text content of error
- `#errorDismiss`: Button to dismiss error (optional)

**State Binding**:
- Visibility driven by `UIState.errorMessage !== null`
- Text content driven by `UIState.errorMessage`

---

## State Management Flow

```
User Click "Start Mic"
    ↓
Request getUserMedia
    ↓
[Permission Granted] → Create AudioContext → Create AnalyserNode
    ↓                                              ↓
Update UIState.microphoneStatus = 'on'     Connect Audio Graph
    ↓                                              ↓
Start Animation Loop                      Begin calculating VolumeLevel
    ↓                                              ↓
requestAnimationFrame                      Update UIState.volumeValue
    ↓                                              ↓
Update DOM Elements  ←─────────────────────────────┘
    ↓
[Loop continues until stopped]
    ↓
User Click "Stop"
    ↓
Stop Audio Tracks → Close AudioContext → Cancel Animation
    ↓
Update UIState.microphoneStatus = 'off'
```

---

## Error States

### Permission Denied

**Trigger**: User clicks "Deny" on browser permission prompt

**State Changes**:
```javascript
UIState = {
  microphoneStatus: 'error',
  errorMessage: 'Microphone access denied. Click the camera icon...',
  volumeValue: 0,
  animationId: null
}
```

### No Microphone Found

**Trigger**: No audio input devices available

**State Changes**: Similar to Permission Denied, different error message

### Browser Not Supported

**Trigger**: getUserMedia or AudioContext not available

**State Changes**: Detected on page load, prevents Start button from functioning

---

## Data Persistence

**None**: This application has zero data persistence.

- No localStorage usage
- No cookies
- No IndexedDB
- No server communication
- Audio data discarded immediately after volume calculation

**Rationale**: Aligns with Constitution Principle VIII (Privacy & No Data Collection)

---

## Performance Characteristics

| Entity | Creation Cost | Memory Usage | Update Frequency |
|--------|---------------|--------------|------------------|
| AudioStream | ~100ms (user interaction) | Minimal (browser managed) | Continuous while active |
| AudioContext | ~10ms | ~1-2MB | N/A (singleton) |
| AnalyserNode | <1ms | ~4KB (2048 samples) | N/A (provides data on demand) |
| VolumeLevel | <1ms | ~4KB (calculation buffer) | 10 Hz (100ms interval) |
| UIState | <1ms | <1KB | 10 Hz |
| DOM Updates | ~1-2ms | N/A | 10 Hz (numeric), 60 Hz (visual bar) |

**Total Memory Footprint**: <5MB (well within constraints)

---

## Validation Summary

All entities satisfy the following criteria:
- ✅ No external data sources (browser APIs only)
- ✅ No persistence mechanisms
- ✅ Clear lifecycle management
- ✅ Minimal memory footprint
- ✅ Efficient update patterns
- ✅ Privacy-compliant (no data retention)

Ready for implementation in Phase 2 (Tasks).
