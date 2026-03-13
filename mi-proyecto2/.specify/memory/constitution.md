<!--
Sync Impact Report:
- Version change: Initial → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections: All core principles, Technical Constraints, Documentation Standards, Governance
- Removed sections: N/A
- Templates requiring updates: ✅ All synchronized with initial constitution
- Follow-up TODOs: None
-->

# Mic Dashboard Constitution

## Core Principles

### I. Educational Simplicity (NON-NEGOTIABLE)
This project MUST remain educational and accessible for students.
- All code must be beginner-friendly with clear, pedagogical structure
- Implementation should demonstrate fundamental web development concepts
- Complexity must be minimized; advanced techniques only when educational value is clear
- Every feature should serve as a learning opportunity

**Rationale**: The primary purpose is education, not production-grade sophistication.

### II. Vanilla Web Technologies Only
This project MUST use only HTML, CSS, and vanilla JavaScript.
- No frameworks (React, Vue, Angular, etc.) are permitted
- No build tools or transpilers required
- No external dependencies beyond browser Web APIs
- Pure web standards to maximize learning and reduce cognitive load

**Rationale**: Students learn core web fundamentals before frameworks; reduces setup complexity.

### III. Local Server Deployment
The application MUST run through a local web server, never by direct file opening.
- No `file://` protocol usage allowed
- Development instructions must include simple server setup (e.g., Python's http.server, Live Server)
- All resource loading must work correctly in server context
- CORS and security context requirements must be documented

**Rationale**: getUserMedia API and other modern Web APIs require secure contexts (HTTPS or localhost).

### IV. Standard Web APIs Only
All browser functionality MUST use standard, widely-supported Web APIs.
- getUserMedia API for microphone access (NON-NEGOTIABLE)
- Web Audio API for audio processing and visualization
- No proprietary or experimental APIs unless clearly marked and optional
- Feature detection and graceful degradation required

**Rationale**: Ensures cross-browser compatibility and teaches industry-standard APIs.

### V. Clear Code Documentation
All code MUST be well-commented with descriptive naming conventions.
- Every function must have a comment explaining its purpose
- Complex logic blocks require inline explanatory comments
- Variable and function names must be self-documenting (no single letters except loop counters)
- Comments should explain "why" not just "what"

**Rationale**: Educational codebase must be readable and instructive for students.

### VI. Comprehensive README
The project MUST include a complete README with setup instructions.
- Step-by-step execution instructions (how to start local server)
- Browser microphone permission requirements and troubleshooting
- Supported browsers and feature requirements documented
- Learning objectives and code walkthrough sections
- Prerequisites and environment setup clearly stated

**Rationale**: Students need clear guidance to successfully run and understand the project.

### VII. Robust Error Handling
The application MUST handle all error scenarios gracefully.
- Microphone permission denial must show user-friendly message
- Browser incompatibility must be detected and reported
- getUserMedia errors must be caught and explained to user
- No silent failures; all errors logged to console for debugging

**Rationale**: Teaches proper error handling patterns; improves user experience.

### VIII. Privacy & No Data Collection
Audio data MUST NOT be recorded, transmitted, or stored.
- Audio stream used exclusively for real-time visualization
- No audio data persistence to disk, memory buffers, or network
- Clear privacy statement in README and UI
- Only visualization calculations performed; original audio discarded immediately

**Rationale**: Respects user privacy; focuses scope on visualization only; teaches ethical data handling.

## Technical Constraints

### Technology Stack
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **APIs**: getUserMedia, Web Audio API (AnalyserNode, AudioContext)
- **Server**: Any simple static file server (Python http.server, Node's http-server, VS Code Live Server)
- **Browsers**: Modern browsers with Web Audio API support (Chrome, Firefox, Safari, Edge)

### Performance Standards
- Visualization must update smoothly (target 60fps or animation frame rate)
- Minimal CPU usage; efficient audio processing loop
- Resource cleanup when visualization stops or page unloads

## Documentation Standards

### Code Comments
Every JavaScript file must begin with a file-level comment describing its purpose.
Functions must follow this comment pattern:
```javascript
/**
 * Brief description of function purpose
 * @param {Type} paramName - Description
 * @returns {Type} Description
 */
```

### README Structure
The README must include these sections (minimum):
1. Project Description & Learning Objectives
2. Prerequisites (browser requirements, basic HTML/CSS/JS knowledge)
3. Setup Instructions (how to start server)
4. How to Use (granting microphone permissions, using controls)
5. Troubleshooting (common errors and solutions)
6. Code Walkthrough (brief explanation of main components)
7. Privacy Statement

## Governance

### Amendment Process
This constitution governs all development decisions for Mic Dashboard.
- Amendments require documented rationale and version increment
- Any deviation from principles must be justified in writing
- Educational value must remain the primary decision criterion

### Versioning
Constitution follows semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Fundamental principle changes or removals
- **MINOR**: New principles added or significant expansions
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance
All code changes must be verified against these principles before merging.
Complexity additions must demonstrate clear educational benefit.

**Version**: 1.0.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19
