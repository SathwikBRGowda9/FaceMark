let video, canvas, ctx;
let isModelLoaded = false;
let faceDetectionInterval = null;

async function initializeFaceDetection() {
    try {
        // Get video and canvas elements
        video = document.getElementById('video');
        canvas = document.getElementById('overlay');
        ctx = canvas.getContext('2d');

        // Load face-api models
        await loadFaceApiModels();
        
        // Start webcam
        await startWebcam();
        
        // Start face detection
        startFaceDetection();
        
        updateStatus('Face detection active', 'success');
    } catch (error) {
        console.error('Error initializing face detection:', error);
        updateStatus('Failed to initialize camera', 'error');
    }
}

async function loadFaceApiModels() {
    try {
        // Load models from CDN
        await faceapi.nets.tinyFaceDetector.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model');
        await faceapi.nets.faceLandmark68Net.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model');
        await faceapi.nets.faceRecognitionNet.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model');
        
        isModelLoaded = true;
        console.log('Face-api models loaded successfully');
    } catch (error) {
        console.error('Error loading face-api models:', error);
        // Fallback: continue without face detection models
        isModelLoaded = false;
    }
}

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 640, 
                height: 480,
                facingMode: 'user'
            } 
        });
        
        video.srcObject = stream;
        
        video.addEventListener('loadedmetadata', () => {
            // Set canvas dimensions to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Ensure canvas overlays video perfectly
            canvas.style.width = '100%';
            canvas.style.height = '100%';
        });
        
    } catch (error) {
        console.error('Error accessing webcam:', error);
        throw new Error('Camera access denied or unavailable');
    }
}

function startFaceDetection() {
    if (faceDetectionInterval) {
        clearInterval(faceDetectionInterval);
    }
    
    faceDetectionInterval = setInterval(async () => {
        if (video.videoWidth > 0 && video.videoHeight > 0) {
            await detectFaces();
        }
    }, 100); // Detect faces every 100ms
}

async function detectFaces() {
    try {
        // Clear previous drawings
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (!isModelLoaded) {
            // Simple fallback face detection using basic webcam
            drawSimpleIndicator();
            return;
        }
        
        // Detect faces using face-api
        const detections = await faceapi.detectAllFaces(
            video, 
            new faceapi.TinyFaceDetectorOptions()
        ).withFaceLandmarks().withFaceDescriptors();
        
        // Draw face detection boxes
        detections.forEach(detection => {
            const box = detection.detection.box;
            drawFaceBox(box.x, box.y, box.width, box.height);
        });
        
        // Update status based on detections
        if (detections.length > 0) {
            updateStatus('Face detected!', 'success');
        } else {
            updateStatus('Looking for face...', 'warning');
        }
        
    } catch (error) {
        console.error('Error detecting faces:', error);
        drawSimpleIndicator();
    }
}

function drawFaceBox(x, y, width, height) {
    // Draw green rectangle around detected face
    ctx.strokeStyle = '#28a745';
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, width, height);
    
    // Draw corner indicators
    const cornerSize = 20;
    ctx.lineWidth = 4;
    
    // Top-left corner
    ctx.beginPath();
    ctx.moveTo(x, y + cornerSize);
    ctx.lineTo(x, y);
    ctx.lineTo(x + cornerSize, y);
    ctx.stroke();
    
    // Top-right corner
    ctx.beginPath();
    ctx.moveTo(x + width - cornerSize, y);
    ctx.lineTo(x + width, y);
    ctx.lineTo(x + width, y + cornerSize);
    ctx.stroke();
    
    // Bottom-left corner
    ctx.beginPath();
    ctx.moveTo(x, y + height - cornerSize);
    ctx.lineTo(x, y + height);
    ctx.lineTo(x + cornerSize, y + height);
    ctx.stroke();
    
    // Bottom-right corner
    ctx.beginPath();
    ctx.moveTo(x + width - cornerSize, y + height);
    ctx.lineTo(x + width, y + height);
    ctx.lineTo(x + width, y + height - cornerSize);
    ctx.stroke();
}

function drawSimpleIndicator() {
    // Draw a simple green circle in the center as fallback
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 50;
    
    ctx.strokeStyle = '#28a745';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Add text
    ctx.fillStyle = '#28a745';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Ready for face detection', centerX, centerY + radius + 25);
}

function updateStatus(message, type) {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = statusIndicator.querySelector('.status-text');
    
    statusText.textContent = message;
    
    // Remove existing status classes
    statusIndicator.classList.remove('text-success', 'text-warning', 'text-danger');
    
    // Add appropriate class based on type
    switch(type) {
        case 'success':
            statusIndicator.classList.add('text-success');
            break;
        case 'warning':
            statusIndicator.classList.add('text-warning');
            break;
        case 'error':
            statusIndicator.classList.add('text-danger');
            break;
    }
}

// Mark attendance function
async function markAttendance() {
    try {
        const markAttendanceBtn = document.getElementById('markAttendanceBtn');
        markAttendanceBtn.disabled = true;
        markAttendanceBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Marking...';
        
        // Capture current frame from video
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        tempCtx.drawImage(video, 0, 0);
        
        // Convert to base64
        const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
        
        // Send to backend
        const response = await fetch('/mark_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update UI with success
            showSuccessModal(result);
            updateStats(result.present_today, result.absent_today);
            updateStatus('Attendance marked successfully!', 'success');
        } else {
            // Show error message
            alert(result.message || 'Failed to mark attendance');
            updateStatus(result.message || 'Failed to mark attendance', 'error');
        }
        
    } catch (error) {
        console.error('Error marking attendance:', error);
        alert('Network error. Please try again.');
        updateStatus('Network error', 'error');
    } finally {
        const markAttendanceBtn = document.getElementById('markAttendanceBtn');
        markAttendanceBtn.disabled = false;
        markAttendanceBtn.innerHTML = '<i class="fas fa-check me-2"></i>Mark Attendance';
    }
}

function showSuccessModal(result) {
    const modal = new bootstrap.Modal(document.getElementById('successModal'));
    const messageElement = document.getElementById('successMessage');
    const detailsElement = document.getElementById('attendanceDetails');
    
    messageElement.textContent = `Welcome, ${result.name}!`;
    detailsElement.innerHTML = `
        <strong>Date:</strong> ${result.date}<br>
        <strong>Time:</strong> ${result.time}
    `;
    
    // Update student photo if provided
    if (result.photo_url) {
        document.getElementById('studentPhoto').src = result.photo_url;
    }
    
    modal.show();
    
    // Auto-close modal after 3 seconds
    setTimeout(() => {
        modal.hide();
    }, 3000);
}

function updateStats(present, absent) {
    document.getElementById('presentCount').textContent = present;
    document.getElementById('absentCount').textContent = absent;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const markAttendanceBtn = document.getElementById('markAttendanceBtn');
    if (markAttendanceBtn) {
        markAttendanceBtn.addEventListener('click', markAttendance);
    }
});

// Clean up when page is unloaded
window.addEventListener('beforeunload', function() {
    if (faceDetectionInterval) {
        clearInterval(faceDetectionInterval);
    }
    
    if (video && video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
    }
});
