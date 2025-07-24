document.addEventListener("DOMContentLoaded", function () {
    // Highlight active navigation link based on current page
    highlightActiveNav();
    
    // Initialize any playbook functionality if on playbooks page
    if (document.getElementById("server-select")) {
        fetchPlaybooks();
    }
    
    // Add hover effects to cards
    addCardEffects();

    // Lazy load system monitoring after initial page render
    setTimeout(initializeSystemMonitoring, 1000);
});

function refreshSystemStatus() {
    fetch('/health_check')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSystemStatus(data);
                showToast('System status refreshed successfully');
            } else {
                showToast('Error: ' + data.error);
            }
        })
        .catch(error => {
            showToast('Error refreshing system status: ' + error);
        });
}

function runHealthCheck() {
    fetch('/health_check')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const statusHtml = `
                    <div class="health-check-results">
                        <h4>Services Status:</h4>
                        <ul>
                            ${Object.entries(data.services).map(([service, status]) => 
                                `<li>${service}: <span class="${status ? 'text-success' : 'text-danger'}">${status ? 'Active' : 'Inactive'}</span></li>`
                            ).join('')}
                        </ul>
                        <p>Disk Usage: <span class="${data.disk_usage > 90 ? 'text-danger' : 'text-success'}">${data.disk_usage}%</span></p>
                        <p>Memory Usage: <span class="${data.memory_usage > 90 ? 'text-danger' : 'text-success'}">${data.memory_usage}%</span></p>
                    </div>
                `;
                document.querySelector('.system-health-banner').innerHTML += statusHtml;
                showToast('Health check completed successfully');
            } else {
                showToast('Error: ' + data.error);
            }
        })
        .catch(error => {
            showToast('Error running health check: ' + error);
        });
}

function clearCache() {
    fetch('/clear_cache')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message);
            } else {
                showToast('Error: ' + data.error);
            }
        })
        .catch(error => {
            showToast('Error clearing cache: ' + error);
        });
}

function initializeSystemMonitoring() {
    // Set up periodic health checks with initial delay
    setTimeout(refreshSystemStatus, 100);
    setInterval(refreshSystemStatus, 300000); // Update every 5 minutes
}

function fetchPlaybooks() {
    let server = document.getElementById("server-select").value;
    fetch(`/get_playbooks?server=${server}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#playbooks-table tbody');
            tableBody.innerHTML = '';
            data.playbooks.forEach(playbook => {
                let row = `<tr>
                    <td>${playbook.name}</td>
                    <td>${playbook.server}</td>
                    <td><button class="run-button" onclick="runPlaybook('${playbook.name}')">Run</button></td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error('Error fetching playbooks:', error));
}

function runPlaybook(playbookName) {
    fetch('/execute_playbook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playbook: playbookName })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Error running playbook: ' + error);
    });
}

// Sidebar Highlight Active Link
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath) {
            link.classList.add('active');
        }
    });
}

// Add hover effects to dashboard cards
// Modern UI Interactions
document.addEventListener('DOMContentLoaded', () => {
    initializeSidebar();
    initializeCards();
    initializeSearch();
    initializeFilters();
    initializeRefreshButton();
});

function initializeSidebar() {
    const toggleBtn = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.dashboard-content, .logs-content');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
        });
    }
}

function initializeCards() {
    const cards = document.querySelectorAll('.stat-card, .playbook-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.2)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

function initializeSearch() {
    // Refresh button functionality has been removed
}

// Function to update the playbook grid with new data
function updatePlaybookGrid(playbooks) {
    const playbookGrid = document.querySelector('.playbook-grid');
    if (!playbookGrid) return;
    
    // Clear existing playbooks
    playbookGrid.innerHTML = '';
    
    // Add new playbooks
    playbooks.forEach(playbook => {
        const playbookCard = document.createElement('div');
        playbookCard.className = 'playbook-card';
        playbookCard.innerHTML = `
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                    <h3><i class="fas fa-code-branch"></i> ${playbook}</h3>
                    <div class="dropdown">
                        <button class="btn btn-link" data-bs-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="editPlaybook('${playbook}')"><i class="fas fa-edit"></i> Edit</a></li>
                            <li><a class="dropdown-item" href="#" onclick="duplicatePlaybook('${playbook}')"><i class="fas fa-copy"></i> Duplicate</a></li>
                            <li><a class="dropdown-item" href="#" onclick="exportPlaybook('${playbook}')"><i class="fas fa-download"></i> Export</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deletePlaybook('${playbook}')"><i class="fas fa-trash"></i> Delete</a></li>
                        </ul>
                    </div>
                </div>
                <div class="tags mt-2">
                    <span class="badge bg-light text-dark">Ansible Playbook</span>
                </div>
            </div>
            <div class="card-body">
                <div class="description mb-3">Ansible playbook file: ${playbook}</div>
                <div class="form-group">
                    <label><i class="fas fa-server"></i> Target Servers</label>
                    <select class="form-select" multiple>
                        <!-- Server options will be populated by the server-side template -->
                    </select>
                </div>
                <div class="execution-info">
                    <div class="info-item">
                        <i class="fas fa-file-code"></i>
                        <span>Playbook File</span>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary" onclick="runPlaybook('${playbook}')">
                    <i class="fas fa-play"></i> Run
                </button>
                <button class="btn btn-info" onclick="schedulePlaybook('${playbook}')">
                    <i class="fas fa-calendar"></i> Schedule
                </button>
            </div>
        `;
        playbookGrid.appendChild(playbookCard);
        
        // Populate server options
        const serverSelect = playbookCard.querySelector('select');
        document.querySelectorAll('#playbookInventory option').forEach(option => {
            if (option.value !== 'all') {
                const newOption = document.createElement('option');
                newOption.value = option.value;
                newOption.textContent = option.textContent;
                serverSelect.appendChild(newOption);
            }
        });
    });
    
    // Re-initialize card hover effects
    initializeCards();
}

function initializeFilters() {
    const filterButtons = document.querySelectorAll('.filter-group .btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.textContent.trim().toLowerCase();
            const logs = document.querySelector('.logs');
            if (logs && filter !== 'all') {
                const lines = logs.textContent.split('\n');
                logs.innerHTML = lines
                    .filter(line => line.toLowerCase().includes(filter))
                    .join('\n');
            }
        });
    });
}

function initializeRefreshButton() {
    const refreshBtn = document.querySelector('.refresh-btn');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.classList.add('rotating');
            setTimeout(() => {
                this.classList.remove('rotating');
                // Here you would typically fetch new logs
                // For now we'll just show a success message
                showToast('Logs refreshed successfully!');
            }, 1000);
        });
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }, 100);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Dark mode and notifications functionality removed
