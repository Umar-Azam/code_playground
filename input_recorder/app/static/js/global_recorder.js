class GlobalRecorder {
    constructor() {
        // Core recording state
        this.recording = false;
        this.startTime = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.events = [];
        
        // Statistics tracking
        this.stats = {
            clicks: 0,
            keys: 0,
            screenTime: 0
        };

        // Initialize UI elements
        this.initializeUI();
        
        // Bind event handlers
        this.bindEventHandlers();
        
        // Initialize update loops
        this.initializeUpdateLoops();
    }

    initializeUI() {
        this.ui = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            status: document.getElementById('status'),
            eventLog: document.getElementById('eventLog'),
            preview: document.getElementById('preview'),
            stats: {
                clicks: document.getElementById('clickCount'),
                keys: document.getElementById('keyCount'),
                position: document.getElementById('lastPosition'),
                time: document.getElementById('recordingTime')
            }
        };
    }

    bindEventHandlers() {
        // UI controls
        this.ui.startBtn.addEventListener('click', () => this.startRecording());
        this.ui.stopBtn.addEventListener('click', () => this.stopRecording());

        // Bind input handlers with context preservation
        this.handleGlobalClick = this.handleGlobalClick.bind(this);
        this.handleGlobalKey = this.handleGlobalKey.bind(this);
    }

    initializeUpdateLoops() {
        // Update recording time every second
        setInterval(() => this.updateRecordingTime(), 1000);
    }

    async startRecording() {
        try {
            // Request screen capture
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: 'always',
                    frameRate: 30
                },
                audio: false
            });

            // Configure video preview
            this.ui.preview.srcObject = screenStream;

            // Initialize MediaRecorder with optimized settings
            this.mediaRecorder = new MediaRecorder(screenStream, {
                mimeType: 'video/webm;codecs=vp9',
                videoBitsPerSecond: 2500000 // 2.5 Mbps
            });

            // Handle recorded chunks
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };

            // Start recording components
            this.mediaRecorder.start(1000); // 1-second chunks
            this.startGlobalTracking();

            // Update UI state
            this.updateUIForRecording(true);

        } catch (error) {
            console.error('Failed to start recording:', error);
            this.ui.status.textContent = 'Error: ' + error.message;
        }
    }

    startGlobalTracking() {
        // Reset state
        this.recording = true;
        this.startTime = Date.now();
        this.events = [];
        this.stats = { clicks: 0, keys: 0, screenTime: 0 };

        // Add global event listeners
        window.addEventListener('click', this.handleGlobalClick, true);
        window.addEventListener('keydown', this.handleGlobalKey, true);
    }

    async stopRecording() {
        if (!this.recording) return;

        // Stop media recording
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.ui.preview.srcObject.getTracks().forEach(track => track.stop());
        }

        // Stop global tracking
        this.stopGlobalTracking();

        // Update UI
        this.updateUIForRecording(false);

        // Prepare and save recording data
        await this.saveRecording();
    }

    stopGlobalTracking() {
        this.recording = false;
        window.removeEventListener('click', this.handleGlobalClick, true);
        window.removeEventListener('keydown', this.handleGlobalKey, true);
    }

    async saveRecording() {
        this.ui.status.textContent = 'Saving recording...';

        try {
            // Prepare form data with both video and event data
            const formData = new FormData();
            
            // Add video blob
            const videoBlob = new Blob(this.recordedChunks, { type: 'video/webm' });
            formData.append('video', videoBlob, 'screen_recording.webm');

            // Add input events data
            const eventsBlob = new Blob([JSON.stringify({
                startTime: this.startTime,
                endTime: Date.now(),
                events: this.events,
                stats: this.stats
            })], { type: 'application/json' });
            formData.append('events', eventsBlob, 'input_events.json');

            // Send to server
            const response = await fetch('/api/save-recording', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.ui.status.textContent = `Recording saved successfully! ID: ${result.recordingId}`;
            } else {
                throw new Error(result.message || 'Failed to save recording');
            }

        } catch (error) {
            console.error('Error saving recording:', error);
            this.ui.status.textContent = 'Error saving recording: ' + error.message;
        }

        // Reset recording state
        this.recordedChunks = [];
        this.events = [];
    }

    handleGlobalClick(event) {
        if (!this.recording) return;

        const eventData = {
            type: 'click',
            timestamp: Date.now() - this.startTime,
            x: event.screenX,
            y: event.screenY,
            target: this.getTargetInfo(event.target)
        };

        this.events.push(eventData);
        this.stats.clicks++;
        
        this.logEvent(`Click at screen position (${event.screenX}, ${event.screenY})`);
        this.updateStats();
    }

    handleGlobalKey(event) {
        if (!this.recording) return;

        // Skip modifier keys
        if (['Control', 'Alt', 'Shift', 'Meta'].includes(event.key)) return;

        const eventData = {
            type: 'keydown',
            timestamp: Date.now() - this.startTime,
            key: event.key,
            code: event.code,
            target: this.getTargetInfo(event.target)
        };

        this.events.push(eventData);
        this.stats.keys++;
        
        this.logEvent(`Key: ${event.key}`);
        this.updateStats();
    }

    getTargetInfo(target) {
        return {
            tag: target.tagName?.toLowerCase() || 'unknown',
            id: target.id || undefined,
            class: target.className || undefined,
            type: target.type || undefined
        };
    }

    updateUIForRecording(isRecording) {
        this.ui.startBtn.classList.toggle('hidden', isRecording);
        this.ui.stopBtn.classList.toggle('hidden', !isRecording);
        this.ui.status.textContent = isRecording ? 'Recording...' : 'Ready';
        
        if (!isRecording) {
            this.ui.eventLog.innerHTML = '';
        }
    }

    logEvent(message) {
        const timestamp = ((Date.now() - this.startTime) / 1000).toFixed(2);
        const logEntry = document.createElement('div');
        logEntry.textContent = `${timestamp}s: ${message}`;
        this.ui.eventLog.insertBefore(logEntry, this.ui.eventLog.firstChild);
    }

    updateStats() {
        this.ui.stats.clicks.textContent = this.stats.clicks;
        this.ui.stats.keys.textContent = this.stats.keys;
    }

    updateRecordingTime() {
        if (this.recording && this.startTime) {
            const duration = Math.floor((Date.now() - this.startTime) / 1000);
            this.ui.stats.time.textContent = `${duration}s`;
            this.stats.screenTime = duration;
        }
    }
}

// Initialize recorder when page loads
document.addEventListener('DOMContentLoaded', () => {
    new GlobalRecorder();
});