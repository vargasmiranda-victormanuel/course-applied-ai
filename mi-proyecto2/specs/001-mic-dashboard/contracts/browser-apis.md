# Browser API Contracts

**Feature**: 001-mic-dashboard  
**Purpose**: Document Web API interfaces used by Mic Dashboard

---

## Overview

This application uses browser Web APIs exclusively. There are no REST endpoints, GraphQL schemas, or custom API contracts. This document serves as reference documentation for the browser APIs we depend on.

---

## getUserMedia API

**Specification**: [W3C Media Capture and Streams](https://www.w3.org/TR/mediacapture-streams/)

**Interface**: `navigator.mediaDevices.getUserMedia(constraints)`

### Request

```typescript
interface MediaStreamConstraints {
  audio: boolean | MediaTrackConstraints;
  video?: boolean | MediaTrackConstraints;
}

// Our usage:
const constraints = { audio: true };
```

### Response

**Success**: Returns `Promise<MediaStream>`
```typescript
interface MediaStream {
  id: string;
  active: boolean;
  getTracks(): MediaStreamTrack[];
  getAudioTracks(): MediaStreamTrack[];
  // ... other methods
}
```

**Errors**: Promise rejection with `DOMException`
- `NotAllowedError`: User denied permission
- `NotFoundError`: No matching device found
- `NotReadableError`: Device already in use
- `NotSupportedError`: Constraints not supported
- `OverconstrainedError`: Constraints cannot be satisfied

### Example Usage
```javascript
try {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // Use stream with Web Audio API
} catch (error) {
  if (error.name === 'NotAllowedError') {
    // Handle permission denial
  }
}
```

---

## Web Audio API - AudioContext

**Specification**: [W3C Web Audio API](https://www.w3.org/TR/webaudio/)

**Interface**: `new AudioContext()`

### Constructor

```typescript
interface AudioContextOptions {
  latencyHint?: 'interactive' | 'balanced' | 'playback' | number;
  sampleRate?: number;
}

// Our usage (default options):
const audioContext = new AudioContext();
```

### Properties

```typescript
interface AudioContext extends BaseAudioContext {
  readonly state: 'suspended' | 'running' | 'closed';
  readonly sampleRate: number;
  readonly currentTime: number;
  // ... other properties
}
```

### Methods Used

```typescript
createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
close(): Promise<void>;
```

### Example Usage
```javascript
const audioContext = new AudioContext();
const source = audioContext.createMediaStreamSource(stream);
// ... create audio graph
await audioContext.close(); // Cleanup
```

---

## Web Audio API - AnalyserNode

**Interface**: `audioContext.createAnalyser()`

### Creation

```typescript
const analyser: AnalyserNode = audioContext.createAnalyser();
```

### Configuration Properties

```typescript
interface AnalyserNode extends AudioNode {
  fftSize: number;                    // Power of 2 between 32 and 32768
  frequencyBinCount: number;          // Readonly: fftSize / 2
  smoothingTimeConstant: number;      // 0.0 to 1.0
  minDecibels: number;
  maxDecibels: number;
}

// Our configuration:
analyser.fftSize = 2048;
analyser.smoothingTimeConstant = 0.8;
```

### Data Extraction Methods

```typescript
// Time-domain data (waveform) - values 0-255
getByteTimeDomainData(array: Uint8Array): void;

// Frequency-domain data (spectrum) - values 0-255
getByteFrequencyData(array: Uint8Array): void;

// Float versions (not used in our implementation)
getFloatTimeDomainData(array: Float32Array): void;
getFloatFrequencyData(array: Float32Array): void;
```

### Example Usage
```javascript
const analyser = audioContext.createAnalyser();
analyser.fftSize = 2048;

const bufferLength = analyser.fftSize;
const dataArray = new Uint8Array(bufferLength);

// In animation loop:
analyser.getByteTimeDomainData(dataArray);
// Process dataArray to calculate volume
```

---

## Animation Frame API

**Specification**: [W3C Timing Control for Script-Based Animations](https://www.w3.org/TR/animation-timing/)

**Interface**: `requestAnimationFrame(callback)`

### Request

```typescript
requestAnimationFrame(callback: FrameRequestCallback): number;

type FrameRequestCallback = (timestamp: DOMHighResTimeStamp) => void;
```

**Returns**: Animation frame request ID (number)

### Cancellation

```typescript
cancelAnimationFrame(id: number): void;
```

### Example Usage
```javascript
let animationId = null;

function animate(timestamp) {
  animationId = requestAnimationFrame(animate);
  
  // Perform visualization updates
  updateVolume();
  updateUI();
}

// Start animation
animationId = requestAnimationFrame(animate);

// Stop animation
cancelAnimationFrame(animationId);
```

---

## Audio Graph Connection Pattern

### Complete Audio Processing Graph

```
MediaStream (from getUserMedia)
    ↓
MediaStreamAudioSourceNode (created from stream)
    ↓
AnalyserNode (configured for time-domain analysis)
    ↓
(no destination - we only read data, don't output audio)
```

### Implementation
```javascript
// 1. Get microphone stream
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// 2. Create audio context
const audioContext = new AudioContext();

// 3. Create source from stream
const source = audioContext.createMediaStreamSource(stream);

// 4. Create analyser
const analyser = audioContext.createAnalyser();
analyser.fftSize = 2048;
analyser.smoothingTimeConstant = 0.8;

// 5. Connect nodes
source.connect(analyser);
// Note: We don't connect to audioContext.destination
// because we don't want audio playback, only analysis

// 6. Read data in animation loop
const dataArray = new Uint8Array(analyser.fftSize);
function readVolume() {
  analyser.getByteTimeDomainData(dataArray);
  // Calculate volume from dataArray
}
```

---

## Browser Compatibility Requirements

### Minimum Browser Versions

| API | Chrome | Firefox | Safari | Edge |
|-----|--------|---------|--------|------|
| getUserMedia | 53 | 36 | 11 | 12 |
| AudioContext | 35 | 25 | 14.1 | 79 |
| AnalyserNode | 35 | 25 | 14.1 | 79 |
| requestAnimationFrame | 24 | 23 | 6.1 | 12 |

**Recommended**: Chrome 60+, Firefox 55+, Safari 11+, Edge 79+

### Feature Detection

```javascript
// getUserMedia
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
  console.error('getUserMedia not supported');
}

// AudioContext (with vendor prefix fallback)
const AudioContextClass = window.AudioContext || window.webkitAudioContext;
if (!AudioContextClass) {
  console.error('Web Audio API not supported');
}

// requestAnimationFrame
if (!window.requestAnimationFrame) {
  console.error('requestAnimationFrame not supported');
}
```

---

## Security Requirements

### Secure Context

getUserMedia requires a **secure context**:
- ✅ `https://` (production)
- ✅ `http://localhost` or `http://127.0.0.1` (development)
- ❌ `file://` protocol (NOT ALLOWED)
- ❌ `http://` on non-localhost domains (NOT ALLOWED)

### Permissions Policy

Modern browsers require user gesture (click) before requesting microphone access. Cannot automatically request on page load.

```javascript
// ✅ Good: Called from button click event
startButton.addEventListener('click', async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
});

// ❌ Bad: Called on page load (may be blocked)
window.addEventListener('load', async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
});
```

---

## Error Handling Contract

### Error Categories

All Web API errors handled with try-catch or promise rejection:

```javascript
try {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // Success path
} catch (error) {
  // Map error.name to user-friendly messages
  switch (error.name) {
    case 'NotAllowedError':
      showError('Microphone access denied.');
      break;
    case 'NotFoundError':
      showError('No microphone found.');
      break;
    case 'NotReadableError':
      showError('Microphone already in use.');
      break;
    case 'NotSupportedError':
      showError('Browser does not support this feature.');
      break;
    default:
      showError('An unexpected error occurred.');
      console.error('getUserMedia error:', error);
  }
}
```

---

## Data Types & Formats

### Audio Sample Values

**Time-Domain Data** (from `getByteTimeDomainData`):
- Type: `Uint8Array`
- Range: 0-255
- Center point: 128 (silence)
- Values < 128: Negative amplitude
- Values > 128: Positive amplitude

**RMS Calculation** (our implementation):
```javascript
// Normalize to -1.0 to +1.0 range
const normalized = (sample - 128) / 128;

// Calculate RMS
const rms = Math.sqrt(sumOfSquares / sampleCount);

// Scale to 0-100
const volume = Math.min(100, Math.floor(rms * 100 * 3));
```

---

## Contract Verification

All browser API contracts verified against:
- ✅ W3C specifications (getUserMedia, Web Audio API)
- ✅ MDN Web Docs compatibility tables
- ✅ Can I Use browser support data
- ✅ Manual testing in target browsers

No custom API contracts required - browser APIs are the contract.
