# Feature Specification: Mic Dashboard

**Feature Branch**: `001-mic-dashboard`  
**Created**: 2026-02-19  
**Status**: Draft  
**Input**: User description: "Construye una aplicación web llamada Mic Dashboard. Objetivo: Un dashboard en HTML que permita activar el micrófono y visualizar el nivel de volumen en tiempo real."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Activate Microphone and View Real-Time Volume (Priority: P1)

A student opens the Mic Dashboard in their browser to learn how the Web Audio API works. They click the "Start Mic" button and immediately see their microphone volume level displayed as both a numeric value (0-100) and an animated progress bar. The visualization updates smoothly in real-time as they speak, whisper, or make sounds near the microphone.

**Why this priority**: This is the core value proposition - real-time audio visualization. Without this, the application has no purpose. This is the minimal viable product that demonstrates getUserMedia and Web Audio API functionality.

**Independent Test**: Can be fully tested by clicking "Start Mic", granting microphone permission, and verifying that speaking into the microphone produces visible changes in both the numeric display and progress bar. Delivers educational value by demonstrating browser audio capture and visualization.

**Acceptance Scenarios**:

1. **Given** the page is loaded, **When** user clicks "Start Mic" button and grants microphone permission, **Then** the status changes to "Mic ON" and volume visualization starts updating
2. **Given** microphone is active, **When** user makes sound near the microphone, **Then** the numeric indicator (0-100) and progress bar reflect the volume level in real-time
3. **Given** microphone is active, **When** user is silent, **Then** the volume indicator shows low values near 0
4. **Given** microphone is active, **When** user speaks loudly, **Then** the volume indicator shows high values approaching 100
5. **Given** microphone is active, **When** 100 milliseconds pass (approximately), **Then** the visualization updates at least once (targeting ~10 updates per second)

---

### User Story 2 - Stop Microphone Capture (Priority: P2)

While using the dashboard, the student wants to pause the audio capture. They click the "Stop" button and the microphone stream immediately stops, the status indicator changes to "Mic OFF", and the visualization freezes or resets.

**Why this priority**: Essential for user control and demonstrates proper resource cleanup. Students learn how to properly release microphone access, which is important for privacy and resource management.

**Independent Test**: Can be fully tested by starting the microphone (P1), then clicking "Stop" and verifying that the microphone indicator light in the browser goes off and the status shows "Mic OFF". Delivers value by teaching resource management.

**Acceptance Scenarios**:

1. **Given** microphone is active ("Mic ON"), **When** user clicks "Stop" button, **Then** the microphone access is released and status changes to "Mic OFF"
2. **Given** microphone has been stopped, **When** user observes the visualization, **Then** it no longer updates (frozen or reset to 0)
3. **Given** microphone has been stopped, **When** user checks browser microphone indicator, **Then** the indicator light is off (browser shows mic is not in use)
4. **Given** microphone has been stopped, **When** user clicks "Start Mic" again, **Then** the microphone can be reactivated successfully

---

### User Story 3 - Handle Permission Denied Gracefully (Priority: P3)

A student opens the dashboard but is concerned about privacy, so they deny microphone permission. Instead of the application breaking or showing confusing errors, they see a clear, friendly message explaining that the microphone is required for the visualization to work and how to grant permission if they change their mind.

**Why this priority**: Critical for user experience and teaches proper error handling. In educational contexts, students need to understand why permissions are required and how to handle user choices gracefully.

**Independent Test**: Can be fully tested by clicking "Start Mic" and selecting "Deny" in the browser's permission prompt. Verifies error handling without requiring any other functionality. Delivers value by teaching permission management and error UX.

**Acceptance Scenarios**:

1. **Given** page is loaded, **When** user clicks "Start Mic" and denies microphone permission, **Then** a clear error message is displayed explaining that microphone access is required
2. **Given** permission has been denied, **When** user reads the error message, **Then** it includes instructions on how to grant permission (browser-specific guidance)
3. **Given** permission error is showing, **When** user remains on the page, **Then** the application remains functional and doesn't crash
4. **Given** permission was previously denied, **When** user refreshes the page and clicks "Start Mic" again, **Then** the browser re-prompts for permission (if browser settings allow)

---

### User Story 4 - Handle Unsupported Browser (Priority: P3)

A student opens the dashboard in an older or unsupported browser that doesn't have getUserMedia API. They immediately see a clear message explaining that their browser doesn't support the required features and suggesting modern alternatives (Chrome, Firefox, Safari, Edge).

**Why this priority**: Prevents confusion and teaches feature detection. Students learn how to handle browser compatibility gracefully and understand that modern Web APIs aren't universally available.

**Independent Test**: Can be tested by temporarily mocking the absence of getUserMedia in the code, or testing in a very old browser. Verifies that the application detects and handles missing API support. Delivers educational value about progressive enhancement and feature detection.

**Acceptance Scenarios**:

1. **Given** page loads in a browser without getUserMedia API, **When** page initializes, **Then** an error message appears explaining browser incompatibility
2. **Given** browser is unsupported, **When** user reads the error message, **Then** it lists compatible browsers (Chrome, Firefox, Safari, Edge)
3. **Given** browser is unsupported, **When** user tries to click "Start Mic", **Then** the button is disabled or shows the same compatibility error
4. **Given** getUserMedia is available but Web Audio API is not, **When** page loads, **Then** appropriate error message indicates which API is missing

---

### Edge Cases

- What happens when user switches between browser tabs while microphone is active? The visualization should continue updating (or optionally pause based on Page Visibility API)
- How does the system handle when user revokes microphone permission while it's actively in use? Should display error message and stop gracefully
- What happens if the microphone hardware is disconnected during active use? Should detect stream ending and show appropriate error
- How does the visualization handle extremely loud sounds that could cause clipping? Values should cap at 100, demonstrating proper bounds checking
- What happens when user rapidly clicks "Start" and "Stop" buttons? Should handle state transitions gracefully without errors or race conditions
- How does the application behave when running from file:// protocol instead of a server? Should detect insecure context and display clear error about needing local server

## Requirements *(mandatory)*

### Functional Requirements

#### Core Microphone Functionality
- **FR-001**: System MUST provide a "Start Mic" button that requests microphone permission via getUserMedia API
- **FR-002**: System MUST provide a "Stop" button that releases the active microphone stream
- **FR-003**: System MUST display current microphone status as either "Mic ON" or "Mic OFF"
- **FR-004**: System MUST capture audio from the default microphone device only (no audio recording or storage)

#### Real-Time Visualization
- **FR-005**: System MUST display volume level as a numeric value ranging from 0 to 100
- **FR-006**: System MUST display volume level as a visual progress bar that updates in sync with the numeric value
- **FR-007**: System MUST update the volume visualization approximately 10 times per second (100ms intervals minimum)
- **FR-008**: System MUST calculate volume level using Web Audio API's AnalyserNode
- **FR-009**: Volume level calculation MUST be based on audio amplitude (RMS or peak values from frequency data)

#### Error Handling & User Feedback
- **FR-010**: System MUST display a clear error message when user denies microphone permission
- **FR-011**: System MUST display a clear error message when browser doesn't support getUserMedia API
- **FR-012**: System MUST display a clear error message when browser doesn't support Web Audio API
- **FR-013**: Error messages MUST include actionable guidance (which browsers to use, how to grant permissions)
- **FR-014**: System MUST detect insecure context (file:// protocol) and display error indicating local server requirement
- **FR-015**: All errors MUST be logged to browser console for debugging purposes

#### Code Organization & Quality
- **FR-016**: Application MUST be structured as three separate files: index.html, styles.css, and app.js
- **FR-017**: Application MUST NOT use any external libraries or frameworks
- **FR-018**: All JavaScript code MUST include explanatory comments for educational purposes
- **FR-019**: Functions and variables MUST use clear, descriptive names
- **FR-020**: HTML structure MUST use semantic elements

#### Deployment & Execution
- **FR-021**: Application MUST run from a local web server (localhost or 127.0.0.1)
- **FR-022**: Application MUST NOT function correctly when opened via file:// protocol (by design, due to secure context requirement)
- **FR-023**: README MUST include step-by-step instructions for starting a local server

#### Privacy & Data Handling
- **FR-024**: Application MUST NOT record audio to any storage medium
- **FR-025**: Application MUST NOT transmit audio data over the network
- **FR-026**: Application MUST NOT persist any audio data in memory beyond what's needed for real-time visualization
- **FR-027**: Application MUST only perform calculations for volume level visualization
- **FR-028**: README MUST include a clear privacy statement explaining that no audio is recorded or saved

### Key Entities

- **AudioStream**: Represents the live microphone input obtained via getUserMedia; contains audio tracks that provide real-time audio data
- **AudioContext**: Web Audio API context that processes the audio stream; manages the audio processing graph
- **AnalyserNode**: Audio processing node that provides frequency and time-domain audio data; used to calculate volume levels
- **VolumeLevel**: Numeric representation (0-100) of current audio amplitude; calculated from AnalyserNode data and displayed to user

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully activate microphone and see volume visualization within 5 seconds of clicking "Start Mic" (assuming permission is granted immediately)
- **SC-002**: Volume visualization updates smoothly at 8-12 times per second, providing perceived real-time feedback
- **SC-003**: Application provides clear, actionable error messages for 100% of error scenarios (permission denied, unsupported browser, insecure context)
- **SC-004**: 90% of students can successfully set up and run the application using only the README instructions (no additional support needed)
- **SC-005**: Application functions correctly across modern browsers (Chrome 60+, Firefox 55+, Safari 11+, Edge 79+)
- **SC-006**: Code readability score: every function and non-trivial code block has explanatory comments (100% coverage for educational clarity)
- **SC-007**: Privacy compliance: zero audio data persistence - verified by code review showing no recording, storage, or transmission functionality
- **SC-008**: Performance: CPU usage remains below 5% on typical student laptop hardware during active visualization
- **SC-009**: Students can identify and explain at least 3 Web APIs used in the code after reviewing the implementation (getUserMedia, Web Audio API, requestAnimationFrame)
- **SC-010**: Application handles all user interaction edge cases without crashing or entering error states (rapid button clicks, permission revocation, browser tab switching)
