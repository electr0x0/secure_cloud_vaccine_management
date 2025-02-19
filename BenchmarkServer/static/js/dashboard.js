
let responseTimeChart, successRateChart;
let currentTestData = {
    durations: [],
    successes: 0,
    failures: 0,
    total: 0
};


let isPollingLogs = false;
let logPollingInterval;
let isRunningTest = false;


let lastSeenLogs = new Set();


document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    updateMetrics(); 
    refreshHistory();
    
    
    startLogPolling();
    
    
    const form = document.getElementById('benchmarkForm');
    form.addEventListener('submit', handleFormSubmit);
});

function initializeCharts() {
    
    responseTimeChart = new ApexCharts(document.querySelector("#responseTimeChart"), {
        chart: {
            type: 'bar',
            height: 300,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: true,
                barHeight: '70%',
            }
        },
        series: [{
            name: 'Duration',
            data: []
        }],
        xaxis: {
            type: 'numeric',
            title: {
                text: 'Duration (seconds)'
            }
        },
        yaxis: {
            labels: {
                formatter: function(value) {
                    return value; // Will be test name
                }
            }
        },
        tooltip: {
            custom: function({ seriesIndex, dataPointIndex, w }) {
                const data = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
                return `
                    <div class="p-2">
                        <div><strong>${data.meta.type}</strong></div>
                        <div>Requests: ${data.meta.requests}</div>
                        <div>Duration: ${data.y.toFixed(2)}s</div>
                    </div>
                `;
            }
        },
        colors: ['#4285f4']
    });
    responseTimeChart.render();

    // Success/Failure Distribution Chart
    successRateChart = new ApexCharts(document.querySelector("#successRateChart"), {
        chart: {
            type: 'donut',
            height: 300
        },
        series: [0, 0, 0, 0],
        labels: ['Encrypt Success', 'Encrypt Failed', 'Decrypt Success', 'Decrypt Failed'],
        colors: ['#00c851', '#ff4444', '#33b5e5', '#ff8800'],
        legend: {
            position: 'bottom',
            formatter: function(label, opts) {
                return `${label}: ${opts.w.globals.series[opts.seriesIndex].toFixed(0)}`;
            }
        },
        tooltip: {
            y: {
                formatter: function(value) {
                    return `${value.toFixed(0)} requests`;
                }
            }
        }
    });
    successRateChart.render();
}


function startLogPolling() {
    if (!isPollingLogs) {
        isPollingLogs = true;
        // Poll immediately first
        pollLogs();
        
        logPollingInterval = setInterval(pollLogs, 2000); // Poll every 2 seconds
    }
}

function stopLogPolling() {
    isPollingLogs = false;
    if (logPollingInterval) {
        clearInterval(logPollingInterval);
    }
}

async function pollLogs() {
    try {
        const response = await fetch('/logs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const logs = await response.json();
        
        if (logs && logs.length > 0) {
            // Check if there are any new logs
            const currentLogs = new Set(logs);
            const hasNewLogs = [...currentLogs].some(log => !lastSeenLogs.has(log));
            
            if (hasNewLogs) {
                updateLogContainer(logs);
                lastSeenLogs = currentLogs;
                
                if (isRunningTest) {
                    updateProgressFromLogs(logs);
                }
            }
        }
    } catch (error) {
        console.error('Failed to fetch logs:', error);
    }
}

function updateLogContainer(logs) {
    const logContainer = document.getElementById('logContainer');
    
    // Only update if we have logs
    if (logs && logs.length > 0) {
        logContainer.innerHTML = '';
        
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            if (log.includes('ERROR')) {
                logEntry.classList.add('error');
            } else if (log.includes('successful')) {
                logEntry.classList.add('success');
            } else {
                logEntry.classList.add('info');
            }
            
            logEntry.textContent = log;
            logContainer.appendChild(logEntry);
        });
        
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

function updateProgressFromLogs(logs) {
    // Extract progress information from logs
    const progressLogs = logs.filter(log => log.includes('Encryption') || log.includes('Decryption'));
    if (progressLogs.length > 0) {
        const lastLog = progressLogs[progressLogs.length - 1];
        const successCount = logs.filter(log => log.includes('successful')).length;
        const failCount = logs.filter(log => log.includes('failed')).length;
        const total = successCount + failCount;
        
        if (total > 0) {
            // Update charts
            updateCharts({
                success: successCount > 0,
                duration: parseFloat(lastLog.match(/took ([\d.]+)ms/)?.[1] || 0)
            });
        }
    }
}

// Update form submission
document.getElementById('benchmarkForm').addEventListener('submit', handleFormSubmit);

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault(); // Prevent page refresh
    
    const formData = new FormData(e.target);
    const data = {
        test_type: formData.get('test_type'),
        num_requests: parseInt(formData.get('num_requests')),
        concurrent_requests: parseInt(formData.get('concurrent_requests')),
        base_url: formData.get('base_url')
    };

    try {
        resetTestData();
        currentTestData.total = data.num_requests;
        isRunningTest = true;

        // Disable the submit button while test is running
        const submitButton = e.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        
        const response = await fetch('/api/benchmark/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.error) {
            showError(result.error);
            isRunningTest = false;
        } else {
            // Start more frequent polling during test
            clearInterval(logPollingInterval);
            logPollingInterval = setInterval(pollLogs, 500); // Poll every 500ms during test
            
            // Wait for test to complete
            await new Promise(resolve => setTimeout(resolve, 1000));
            await refreshHistory();
            await updateMetrics();  // Add metrics update
            
            // Reset polling interval
            clearInterval(logPollingInterval);
            logPollingInterval = setInterval(pollLogs, 2000);
            isRunningTest = false;
        }
    } catch (error) {
        showError(`Failed to start benchmark: ${error.message}`);
        isRunningTest = false;
    } finally {
        // Re-enable the submit button
        const submitButton = e.target.querySelector('button[type="submit"]');
        submitButton.disabled = false;
    }
}

function updateCharts(data) {
    // Update response time chart
    currentTestData.durations.push(data.duration);
    responseTimeChart.updateSeries([{
        data: currentTestData.durations.map((d, i) => [i + 1, d])
    }]);

    // Update success rate chart
    if (data.success) {
        currentTestData.successes++;
    } else {
        currentTestData.failures++;
    }
    successRateChart.updateSeries([
        currentTestData.successes,
        currentTestData.failures,
        currentTestData.successes,
        currentTestData.failures
    ]);
}

function resetTestData() {
    currentTestData = {
        durations: [],
        successes: 0,
        failures: 0,
        total: 0
    };
    lastSeenLogs = new Set(); // Reset last seen logs
    responseTimeChart.updateSeries([{data: []}]);
    successRateChart.updateSeries([0, 0, 0, 0]);
    
    // Clear logs but don't stop polling
    document.getElementById('logContainer').innerHTML = '';
}

async function refreshHistory() {
    try {
        const response = await fetch('/api/benchmark/history');
        const history = await response.json();
        
        const historyTable = document.getElementById('historyTable');
        historyTable.innerHTML = history.map(test => `
            <tr>
                <td>${formatDate(test.timestamp)}</td>
                <td>${test.test_type}</td>
                <td>${test.num_requests}</td>
                <td>${calculateSuccessRate(test)}%</td>
                <td>${test.avg_duration.toFixed(2)}ms</td>
                <td>${test.requests_per_second.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewTestDetails('${test.test_id}')">
                        <i class="fas fa-search"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to refresh history:', error);
    }
}

function calculateSuccessRate(test) {
    return ((test.successful_requests / (test.successful_requests + test.failed_requests)) * 100).toFixed(1);
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleString();
}

async function viewTestDetails(testId) {
    try {
        const response = await fetch(`/api/benchmark/result/${testId}`);
        const result = await response.json();
        
        const modal = new bootstrap.Modal(document.getElementById('testDetailsModal'));
        const detailsDiv = document.getElementById('testDetails');
        
        // Calculate test duration in seconds
        const startTime = new Date(result.start_time);
        const endTime = new Date(result.end_time);
        const durationInSeconds = (endTime - startTime) / 1000;
        
        detailsDiv.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="metric-card bg-light">
                        <div class="metric-value">${result.successful_requests}/${result.total_requests}</div>
                        <div class="metric-label">Successful Requests</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card bg-light">
                        <div class="metric-value">${result.requests_per_second.toFixed(1)}</div>
                        <div class="metric-label">Requests/Second</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card bg-light">
                        <div class="metric-value">${result.avg_duration.toFixed(2)}ms</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card bg-light">
                        <div class="metric-value">${durationInSeconds.toFixed(1)}s</div>
                        <div class="metric-label">Total Duration</div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">Response Time Range</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <div class="small text-muted">Min</div>
                                    <div class="h5">${result.min_duration.toFixed(2)}ms</div>
                                </div>
                                <div>
                                    <div class="small text-muted">Average</div>
                                    <div class="h5">${result.avg_duration.toFixed(2)}ms</div>
                                </div>
                                <div>
                                    <div class="small text-muted">Max</div>
                                    <div class="h5">${result.max_duration.toFixed(2)}ms</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">Test Information</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-6">
                                    <div class="small text-muted">Test ID</div>
                                    <div class="mb-2">${result.test_id}</div>
                                    <div class="small text-muted">Start Time</div>
                                    <div>${new Date(result.start_time).toLocaleString()}</div>
                                </div>
                                <div class="col-6">
                                    <div class="small text-muted">Type</div>
                                    <div class="mb-2">${result.test_type}</div>
                                    <div class="small text-muted">End Time</div>
                                    <div>${new Date(result.end_time).toLocaleString()}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header bg-light d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Detailed Results</h6>
                    <span class="badge bg-primary">${result.detailed_results.length} Requests</span>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive" style="max-height: 400px;">
                        <table class="table table-hover table-striped mb-0">
                            <thead class="sticky-top bg-light">
                                <tr>
                                    <th>#</th>
                                    <th>Status</th>
                                    <th>Duration</th>
                                    <th>Email</th>
                                    <th>Response</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${result.detailed_results.map((r, i) => `
                                    <tr>
                                        <td>${i + 1}</td>
                                        <td>
                                            <span class="badge bg-${r.success ? 'success' : 'danger'}">
                                                ${r.status_code}
                                            </span>
                                        </td>
                                        <td>${r.duration.toFixed(2)}ms</td>
                                        <td>${r.email || 'N/A'}</td>
                                        <td>
                                            <code class="small">
                                                ${r.response ? JSON.parse(r.response).message : r.error || 'N/A'}
                                            </code>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        modal.show();
    } catch (error) {
        console.error('Failed to load test details:', error);
        showError('Failed to load test details');
    }
}

function showError(message) {
    console.error(message);
    const logContainer = document.getElementById('logContainer');
    const errorEntry = document.createElement('div');
    errorEntry.className = 'log-entry error';
    errorEntry.textContent = `Error: ${message}`;
    logContainer.appendChild(errorEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Add cleanup when leaving the page
window.addEventListener('beforeunload', () => {
    stopLogPolling();
});


async function updateMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const metrics = await response.json();

        // Update server latency
        document.getElementById('serverLatency').textContent = `${metrics.server_latency.toFixed(1)}ms`;

        // Update success rates
        const encryptSuccessRate = metrics.encrypt.success_rate.toFixed(1);
        const decryptSuccessRate = metrics.decrypt.success_rate.toFixed(1);
        document.getElementById('successRate').innerHTML = `
            <div>Encrypt: ${encryptSuccessRate}%</div>
            <div>Decrypt: ${decryptSuccessRate}%</div>
        `;

        // Update average response times
        const encryptAvgTime = metrics.encrypt.avg_response_time.toFixed(1);
        const decryptAvgTime = metrics.decrypt.avg_response_time.toFixed(1);
        document.getElementById('avgResponseTime').innerHTML = `
            <div>Encrypt: ${encryptAvgTime}ms</div>
            <div>Decrypt: ${decryptAvgTime}ms</div>
        `;

        // Update requests per second
        const encryptRPS = metrics.encrypt.requests_per_second.toFixed(1);
        const decryptRPS = metrics.decrypt.requests_per_second.toFixed(1);
        document.getElementById('requestsPerSec').innerHTML = `
            <div>Encrypt: ${encryptRPS}</div>
            <div>Decrypt: ${decryptRPS}</div>
        `;

        // Update test durations chart
        const allTestDurations = [
            ...metrics.encrypt.test_durations.map(t => ({
                x: `${t.name} (${t.requests} reqs)`,
                y: t.duration,
                meta: {
                    type: 'Encrypt',
                    requests: t.requests,
                    name: t.name
                }
            })),
            ...metrics.decrypt.test_durations.map(t => ({
                x: `${t.name} (${t.requests} reqs)`,
                y: t.duration,
                meta: {
                    type: 'Decrypt',
                    requests: t.requests,
                    name: t.name
                }
            }))
        ].sort((a, b) => new Date(b.meta.name) - new Date(a.meta.name));

        responseTimeChart.updateSeries([{
            name: 'Test Duration',
            data: allTestDurations
        }]);

        // Update success/failure chart
        const encryptSuccess = metrics.encrypt.total_requests * (metrics.encrypt.success_rate / 100);
        const encryptFail = metrics.encrypt.total_requests - encryptSuccess;
        const decryptSuccess = metrics.decrypt.total_requests * (metrics.decrypt.success_rate / 100);
        const decryptFail = metrics.decrypt.total_requests - decryptSuccess;

        successRateChart.updateSeries([
            Math.round(encryptSuccess),
            Math.round(encryptFail),
            Math.round(decryptSuccess),
            Math.round(decryptFail)
        ]);

    } catch (error) {
        console.error('Failed to update metrics:', error);
        showError('Failed to update metrics');
    }
} 