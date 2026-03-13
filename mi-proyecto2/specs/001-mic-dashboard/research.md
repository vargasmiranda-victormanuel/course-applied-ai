# Research: Mic Dashboard

**Created**: 2026-02-19  
**Feature**: 001-mic-dashboard  
**Purpose**: Best practices and technical decisions for Web Audio API implementation

## Research Topics

### 1. getUserMedia API - Microphone Access Patterns

**Decision**: Use `navigator.mediaDevices.getUserMedia({ audio: true })` with Promise-based error handling

**Rationale**:
- Modern Promise-based API (as opposed to legacy navigator.getUserMedia with callbacks)
- Widely supported in target browsers (Chrome 53+, Firefox 36+, Safari 11+, Edge 12+)
- Returns MediaStream that can be connected to Web Audio API AudioContext
- Provides structured error objects for different failure modes

**Best Practices Applied**:
1. **Feature Detection**: Check for `navigator.mediaDevices` and `getUserMedia` before attempting access
2. **Constraint Object**: Use `{ audio: true }` without additional constraints for maximum compatibility
3. **Error Handling**: Catch distinct error types:
   - `NotAllowedError`: User denied permission
   - `NotFoundError`: No microphone hardware detected
   - `NotSupportedError`: Browser doesn't support the API
   - `NotReadableError`: Hardware already in use by another application
4. **Stream Management**: Store MediaStream reference for proper cleanup (call `.getTracks().forEach(track => track.stop())`)

**Alternatives Considered**:
- Legacy navigator.getUserMedia (callback-based) - Rejected: deprecated, requires vendor prefixes
- Audio element with capture attribute - Rejected: doesn't provide programmatic access to audio data
- MediaRecorder API - Rejected: designed for recording, not real-time visualization

**Code Pattern**:
```javascript
async function requestMicrophoneAccess() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return stream;
  } catch (error) {
    if (error.name === 'NotAllowedError') {
      // Handle permission denial
    } else if (error.name === 'NotFoundError') {
      // Handle no microphone
    }
    // Handle other errors
  }
}
```

---

### 2. Web Audio API - Volume Calculation from AnalyserNode

**Decision**: Use AnalyserNode with `getByteTimeDomainData()` and calculate RMS (Root Mean Square) for volume level

**Rationale**:
- AnalyserNode provides real-time frequency and time-domain analysis without storing audio
- Time-domain data (waveform) is more appropriate for volume than frequency data for this use case
- RMS calculation gives better perceived loudness than peak amplitude
- Byte arrays (Uint8Array) are efficient and simpler for students than Float32Array

**Best Practices Applied**:
1. **AudioContext Creation**: Create once when microphone starts, close when stopped
2. **Graph Setup**: MediaStream → AudioContext.createMediaStreamSource() → AnalyserNode
3. **AnalyserNode Configuration**:
   - `fftSize: 2048` (provides 1024-sample buffer, good balance of resolution vs performance)
   - `smoothingTimeConstant: 0.8` (slight smoothing to reduce jitter in visualization)
4. **Volume Calculation Algorithm**:
   ```javascript
   // Get time-domain data (waveform)
   const dataArray = new Uint8Array(analyser.fftSize);
   analyser.getByteTimeDomainData(dataArray);
   
   // Calculate RMS (Root Mean Square)
   let sum = 0;
   for (let i = 0; i < dataArray.length; i++) {
     const normalized = (dataArray[i] - 128) / 128; // Center around 0
     sum += normalized * normalized;
   }
   const rms = Math.sqrt(sum / dataArray.length);
   
   // Scale to 0-100
   const volume = Math.min(100, Math.floor(rms * 100 * 3)); // *3 multiplier for better sensitivity
   ```
5. **Update Frequency**: Use `requestAnimationFrame()` for smooth 60fps potential, internally throttle to ~10 updates/sec for display

**Alternatives Considered**:
- Peak amplitude detection - Rejected: too sensitive, causes jittery visualization
- Frequency domain (getByteFrequencyData) - Rejected: more complex, overkill for simple volume
- ScriptProcessorNode - Rejected: deprecated in favor of AudioWorkletNode
- AudioWorkletNode - Rejected: too advanced for educational context, requires separate file

**Resource Management**:
- Always call `audioContext.close()` when stopping to release hardware resources
- Disconnect analyser node when not in use
- Time-domain buffer (Uint8Array) is reused, not reallocated each frame

---

### 3. Real-Time Visualization - Animation Loop Pattern

**Decision**: Use `requestAnimationFrame()` with internal throttling for visualization updates

**Rationale**:
- `requestAnimationFrame()` is the browser's native mechanism for smooth animations (60fps)
- Automatically pauses when tab is hidden, saving CPU
- More efficient than `setInterval()` for UI updates
- Allows for smooth progress bar animation while updating numeric display at lower frequency

**Best Practices Applied**:
1. **Animation Loop Structure**:
   ```javascript
   let animationId = null;
   let lastUpdateTime = 0;
   const UPDATE_INTERVAL = 100; // 100ms = 10 updates/sec
   
   function visualize(timestamp) {
     animationId = requestAnimationFrame(visualize);
     
     if (timestamp - lastUpdateTime >= UPDATE_INTERVAL) {
       // Calculate and update volume display
       lastUpdateTime = timestamp;
     }
     
     // Update smooth progress bar animation every frame
     updateProgressBar();
   }
   ```
2. **Cleanup**: Store animation ID and call `cancelAnimationFrame(animationId)` when stopping
3. **Timestamp Usage**: Use requestAnimationFrame's timestamp parameter instead of Date.now() for accuracy
4. **Throttling**: Update numeric display and calculations at 10Hz, but allow progress bar to animate smoothly

**Alternatives Considered**:
- setInterval() - Rejected: doesn't pause when tab hidden, less performant, doesn't align with screen refresh
- setTimeout() recursion - Rejected: same issues as setInterval()
- Pure CSS animations - Rejected: can't be driven by real-time audio data

**Performance Considerations**:
- Request next frame only when mic is active (prevents unnecessary CPU usage when stopped)
- Throttle calculations to necessary frequency (10Hz sufficient for perceived real-time)
- Use integer math where possible (floor, min) instead of floating point

---

### 4. Error Handling & Feature Detection

**Decision**: Implement progressive enhancement with feature detection and user-friendly error messages

**Rationale**:
- Not all browsers support getUserMedia (Safari iOS webview, older browsers)
- Users may deny permissions either in prompt or via browser settings
- Educational context requires clear, actionable error messages
- Feature detection prevents crashes in unsupported environments

**Best Practices Applied**:
1. **Feature Detection on Page Load**:
   ```javascript
   function checkBrowserSupport() {
     if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
       showError('Browser not supported. Please use Chrome, Firefox, Safari, or Edge.');
       return false;
     }
     if (!window.AudioContext && !window.webkitAudioContext) {
       showError('Web Audio API not supported.');
       return false;
     }
     return true;
   }
   ```
2. **Secure Context Detection**:
   ```javascript
   if (window.location.protocol === 'file:') {
     showError('This app must be run from a local server (http://localhost). See README for instructions.');
   }
   ```
3. **User-Friendly Error Messages**: Map technical errors to plain language
   - `NotAllowedError` → "Microphone access denied. Click the camera icon in your browser's address bar to grant permission."
   - `NotFoundError` → "No microphone found. Please connect a microphone and try again."
   - `NotReadableError` → "Microphone is already in use by another application."
4. **Console Logging**: Always log technical error details to console for debugging while showing friendly message to user
5. **Error UI**: Dedicated error display element with distinct styling, stays visible until dismissed

**Alternatives Considered**:
- Silent failures - Rejected: poor UX, violates Constitution Principle VII
- Generic "something went wrong" message - Rejected: not educational, doesn't help users fix issues
- Only console.error() - Rejected: students may not know to open dev tools

**Error Recovery**:
- Provide "Try Again" button after permission denial (in case user wants to grant permission)
- Detect permission state changes and update UI accordingly
- Graceful degradation: app remains functional (doesn't crash) even if mic unavailable

---

### 5. Code Organization & Documentation Strategy

**Decision**: Single-file JavaScript with clearly-commented sections and JSDoc function documentation

**Rationale**:
- Educational simplicity: students can read entire app logic in one file
- No module bundling needed (aligns with Constitution Principle II - no build tools)
- Clear section comments guide students through architecture
- JSDoc provides type hints even without TypeScript

**Best Practices Applied**:
1. **File Structure**:
   ```javascript
   /**
    * Mic Dashboard - Real-time microphone volume visualization
    * Educational project demonstrating getUserMedia and Web Audio API
    */
   
   // ===== GLOBAL STATE =====
   let audioContext = null;
   let analyser = null;
   // ... other state variables
   
   // ===== INITIALIZATION =====
   function init() { /* ... */ }
   
   // ===== MICROPHONE MANAGEMENT =====
   async function startMicrophone() { /* ... */ }
   function stopMicrophone() { /* ... */ }
   
   // ===== AUDIO PROCESSING =====
   function calculateVolume() { /* ... */ }
   
   // ===== VISUALIZATION =====
   function updateDisplay(volume) { /* ... */ }
   function visualize(timestamp) { /* ... */ }
   
   // ===== ERROR HANDLING =====
   function showError(message) { /* ... */ }
   
   // ===== EVENT LISTENERS =====
   document.addEventListener('DOMContentLoaded', init);
   ```
2. **JSDoc Comments**:
   ```javascript
   /**
    * Calculate the current volume level from the analyser node
    * Uses RMS (Root Mean Square) algorithm for perceived loudness
    * @returns {number} Volume level from 0 to 100
    */
   function calculateVolume() { /* ... */ }
   ```
3. **Inline Comments**: Explain "why" not just "what" (e.g., "// *3 multiplier increases sensitivity for typical speaking volumes")
4. **Naming Conventions**: Descriptive names (`startMicrophone` not `start`, `audioContext` not `ctx`)

**Educational Benefits**:
- Students can identify major components at a glance via section comments
- Function documentation teaches JSDoc syntax
- Single file allows full-text search to trace variable usage
- No abstractions hiding implementation details

---

## Technology Stack Summary

| Component | Technology | Version/Standard | Support |
|-----------|-----------|------------------|---------|
| Language | JavaScript | ES6+ (2015) | All modern browsers |
| Audio Input | getUserMedia API | W3C Recommendation | Chrome 53+, Firefox 36+, Safari 11+, Edge 12+ |
| Audio Processing | Web Audio API | W3C Recommendation | Chrome 35+, Firefox 25+, Safari 14.1+, Edge 79+ |
| Animation | requestAnimationFrame | W3C Recommendation | All modern browsers |
| Markup | HTML5 | W3C Recommendation | All modern browsers |
| Styling | CSS3 | W3C Recommendation | All modern browsers |
| Server | Python http.server / Live Server | Python 3+ / VS Code extension | Cross-platform |

---

## Performance Targets Validation

| Metric | Target | Implementation Strategy |
|--------|--------|-------------------------|
| Animation Frame Rate | 60fps | requestAnimationFrame native scheduling |
| Volume Update Rate | 8-12 Hz | Throttle calculations to 100ms intervals |
| CPU Usage | <5% | Efficient RMS calculation, throttled updates, paused when tab hidden |
| Memory Usage | Minimal | Reuse buffers, close AudioContext when stopped |
| Response Latency | <100ms from sound to visual | Direct AnalyserNode connection, no buffering delay |

All targets achievable with proposed implementation approach. No performance concerns identified during research.

---

## Security & Privacy Considerations

1. **Secure Context Requirement**: getUserMedia only works over HTTPS or localhost (enforced by browsers)
2. **User Permission**: Browser prompts for explicit microphone permission (cannot bypass)
3. **No Recording**: Audio data never leaves AnalyserNode, not written to storage or transmitted
4. **Resource Cleanup**: Explicit track.stop() releases microphone access (browser indicator light goes off)
5. **XSS Prevention**: No innerHTML usage, all updates via textContent (low risk given no user input, but good practice)

Privacy compliance with Constitution Principle VIII verified: implementation cannot record, store, or transmit audio data.

---

## Conclusion

All technical decisions align with constitution principles. No clarifications or ambiguities remain. Implementation approach validated:
- ✅ Educational simplicity maintained
- ✅ No external dependencies
- ✅ Standard Web APIs only
- ✅ Comprehensive error handling planned
- ✅ Performance targets achievable
- ✅ Privacy requirements satisfied

Ready to proceed to Phase 1: Design & Contracts.
