// Admin Dashboard JavaScript

let currentFilters = {
    date: '',
    name: ''
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
});

async function initializeDashboard() {
    // Load initial data
    await loadStats();
    await loadUsers();
    await loadAttendanceRecords();
    
    // Set today's date as default filter
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dateFilter').value = today;
    currentFilters.date = today;
}

function setupEventListeners() {
    // Filter buttons
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('exportBtn').addEventListener('click', exportAttendance);
    
    // Date filter change
    document.getElementById('dateFilter').addEventListener('change', function() {
        currentFilters.date = this.value;
    });
    
    // Name filter change
    document.getElementById('nameFilter').addEventListener('change', function() {
        currentFilters.name = this.value;
    });
}

async function loadStats() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`/get_stats?date=${today}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalStudents').textContent = data.total;
            document.getElementById('presentToday').textContent = data.present;
            document.getElementById('absentToday').textContent = data.absent;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/get_users');
        const data = await response.json();
        
        if (data.success) {
            const nameFilter = document.getElementById('nameFilter');
            
            // Clear existing options except "All Students"
            nameFilter.innerHTML = '<option value="">All Students</option>';
            
            // Add user options
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.name;
                option.textContent = user.name;
                nameFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function loadAttendanceRecords() {
    try {
        showLoading(true);
        
        // Build query parameters
        const params = new URLSearchParams();
        if (currentFilters.date) {
            params.append('date', currentFilters.date);
        }
        if (currentFilters.name) {
            params.append('name', currentFilters.name);
        }
        
        const response = await fetch(`/get_all_attendance?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            displayAttendanceRecords(data.records);
        } else {
            showError('Failed to load attendance records');
        }
    } catch (error) {
        console.error('Error loading attendance records:', error);
        showError('Network error while loading records');
    } finally {
        showLoading(false);
    }
}

function displayAttendanceRecords(records) {
    const tableBody = document.getElementById('attendanceTableBody');
    const emptyState = document.getElementById('emptyState');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (records.length === 0) {
        emptyState.classList.remove('d-none');
        return;
    }
    
    emptyState.classList.add('d-none');
    
    // Add rows
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.name}</td>
            <td>${record.date}</td>
            <td>${record.time}</td>
            <td><span class="badge bg-success">Present</span></td>
        `;
        tableBody.appendChild(row);
    });
}

async function applyFilters() {
    // Update filters from form
    currentFilters.date = document.getElementById('dateFilter').value;
    currentFilters.name = document.getElementById('nameFilter').value;
    
    // Reload attendance records with new filters
    await loadAttendanceRecords();
    
    // Update stats for selected date
    if (currentFilters.date) {
        await updateStatsForDate(currentFilters.date);
    }
}

async function updateStatsForDate(date) {
    try {
        const response = await fetch(`/get_stats?date=${date}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('presentToday').textContent = data.present;
            document.getElementById('absentToday').textContent = data.absent;
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function exportAttendance() {
    try {
        const exportBtn = document.getElementById('exportBtn');
        const originalText = exportBtn.innerHTML;
        
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
        
        // Build query parameters
        const params = new URLSearchParams();
        if (currentFilters.date) {
            params.append('date', currentFilters.date);
        }
        
        // Create download link
        const url = `/export_attendance?${params.toString()}`;
        const link = document.createElement('a');
        link.href = url;
        link.download = `attendance_export_${currentFilters.date || 'all'}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        showSuccessMessage('Attendance data exported successfully!');
        
    } catch (error) {
        console.error('Error exporting attendance:', error);
        showError('Failed to export attendance data');
    } finally {
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.disabled = false;
        exportBtn.innerHTML = '<i class="fas fa-download me-2"></i>Export CSV';
    }
}

function showLoading(show) {
    const loadingState = document.getElementById('loadingState');
    const attendanceTable = document.getElementById('attendanceTable');
    
    if (show) {
        loadingState.classList.remove('d-none');
        attendanceTable.style.opacity = '0.5';
    } else {
        loadingState.classList.add('d-none');
        attendanceTable.style.opacity = '1';
    }
}

function showError(message) {
    // Create and show error alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showSuccessMessage(message) {
    // Create and show success alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Auto-refresh stats every 30 seconds
setInterval(async function() {
    await loadStats();
}, 30000);

// Real-time clock update
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    // Update any clock elements if they exist
    const clockElements = document.querySelectorAll('.current-time');
    clockElements.forEach(element => {
        element.textContent = timeString;
    });
}

// Update clock every second
setInterval(updateClock, 1000);
updateClock();
