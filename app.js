document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('resumeFile');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById('results');
    
    if (!fileInput.files[0]) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    // Show loading state
    showLoading(submitBtn, 'Analyzing Resume...');
    resultsDiv.innerHTML = getLoadingSpinner('Analyzing your resume for ATS compatibility...');
    
    formData.append('resume', fileInput.files[0]);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            const scoreColor = result.ats_score >= 80 ? 'success' : result.ats_score >= 60 ? 'warning' : 'danger';
            const scoreIcon = result.ats_score >= 80 ? 'check-circle' : result.ats_score >= 60 ? 'exclamation-triangle' : 'times-circle';
            
            resultsDiv.innerHTML = `
                <div class="card animate-fade-in">
                    <div class="card-header bg-gradient-primary text-white">
                        <h4><i class="fas fa-chart-line pulse"></i> Analysis Results</h4>
                    </div>
                    <div class="card-body text-center">
                        <div class="score-circle mb-4">
                            <div class="score-display text-${scoreColor} animate-count-up" data-target="${result.ats_score}">0%</div>
                            <p class="lead mt-2"><i class="fas fa-${scoreIcon}"></i> ATS Compatibility Score</p>
                        </div>
                        <div class="progress mb-4 progress-animated">
                            <div class="progress-bar bg-${scoreColor} progress-bar-striped progress-bar-animated" 
                                 style="width: 0%" data-width="${result.ats_score}%"></div>
                        </div>
                        <div class="text-start">
                            <h5><i class="fas fa-lightbulb text-warning"></i> Improvement Suggestions:</h5>
                            <ul class="list-group list-group-flush">
                                ${result.feedback.map((item, index) => `
                                    <li class="list-group-item animate-slide-in" style="animation-delay: ${index * 0.1}s">
                                        <i class="fas fa-arrow-right text-primary"></i> ${item}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            // Animate progress bar and score
            setTimeout(() => {
                animateProgressBar(resultsDiv.querySelector('.progress-bar'));
                animateCountUp(resultsDiv.querySelector('.animate-count-up'));
            }, 300);
            
        } else {
            showAlert('Error: ' + result.error, 'danger');
            resultsDiv.innerHTML = '';
        }
    } catch (error) {
        showAlert('Upload failed: ' + error.message, 'danger');
        resultsDiv.innerHTML = '';
    } finally {
        hideLoading(submitBtn, 'Analyze Resume');
    }
});

document.getElementById('jobMatchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const jobDescription = document.getElementById('jobDescription').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById('jobResults');
    
    if (!jobDescription.trim()) {
        showAlert('Please enter a job description', 'warning');
        return;
    }
    
    showLoading(submitBtn, 'Analyzing Match...');
    resultsDiv.innerHTML = getLoadingSpinner('Analyzing job match compatibility...');
    
    try {
        const response = await fetch('/match_job', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_description: jobDescription })
        });
        
        const result = await response.json();
        
        if (result.match_score !== undefined) {
            const matchColor = result.match_score >= 80 ? 'success' : result.match_score >= 60 ? 'warning' : 'danger';
            
            let detailsHtml = '';
            if (result.missing_keywords && result.missing_keywords.length > 0) {
                detailsHtml += `
                    <div class="alert alert-info animate-slide-in">
                        <h6><i class="fas fa-key"></i> Missing Keywords:</h6>
                        <div class="d-flex flex-wrap gap-1">
                            ${result.missing_keywords.slice(0, 10).map((kw, index) => 
                                `<span class="badge bg-secondary animate-fade-in" style="animation-delay: ${index * 0.1}s">${kw}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }
            if (result.strengths && result.strengths.length > 0) {
                detailsHtml += `
                    <div class="alert alert-success animate-slide-in">
                        <h6><i class="fas fa-thumbs-up"></i> Strengths:</h6>
                        <ul class="mb-0">
                            ${result.strengths.map((item, index) => 
                                `<li class="animate-fade-in" style="animation-delay: ${index * 0.1}s">${item}</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }
            if (result.improvements && result.improvements.length > 0) {
                detailsHtml += `
                    <div class="alert alert-warning animate-slide-in">
                        <h6><i class="fas fa-tools"></i> Areas to Improve:</h6>
                        <ul class="mb-0">
                            ${result.improvements.map((item, index) => 
                                `<li class="animate-fade-in" style="animation-delay: ${index * 0.1}s">${item}</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }
            
            resultsDiv.innerHTML = `
                <div class="card animate-fade-in">
                    <div class="card-header bg-gradient-success text-white">
                        <h4><i class="fas fa-bullseye pulse"></i> Job Match Results</h4>
                    </div>
                    <div class="card-body text-center">
                        <div class="score-circle mb-4">
                            <div class="score-display text-${matchColor} animate-count-up" data-target="${result.match_score}">0%</div>
                            <p class="lead mt-2">Job Match Score</p>
                        </div>
                        <div class="progress mb-4 progress-animated">
                            <div class="progress-bar bg-${matchColor} progress-bar-striped progress-bar-animated" 
                                 style="width: 0%" data-width="${result.match_score}%"></div>
                        </div>
                        <div class="text-start">
                            ${detailsHtml}
                        </div>
                    </div>
                </div>
            `;
            
            setTimeout(() => {
                animateProgressBar(resultsDiv.querySelector('.progress-bar'));
                animateCountUp(resultsDiv.querySelector('.animate-count-up'));
            }, 300);
            
        } else {
            showAlert('Error: ' + (result.error || 'Unknown error'), 'danger');
            resultsDiv.innerHTML = '';
        }
    } catch (error) {
        showAlert('Analysis failed: ' + error.message, 'danger');
        resultsDiv.innerHTML = '';
    } finally {
        hideLoading(submitBtn, 'Analyze Match');
    }
});

document.getElementById('coverLetterForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const companyName = document.getElementById('companyName').value;
    const position = document.getElementById('position').value;
    const jobDesc = document.getElementById('jobDescForCover').value;
    const tone = document.getElementById('tone').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById('coverLetterResults');
    
    if (!companyName || !position || !jobDesc) {
        showAlert('Please fill in all fields', 'warning');
        return;
    }
    
    showLoading(submitBtn, 'Generating Letter...');
    resultsDiv.innerHTML = getLoadingSpinner('Crafting your personalized cover letter...');
    
    try {
        const response = await fetch('/generate_cover_letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company_name: companyName,
                position: position,
                job_description: jobDesc,
                tone: tone
            })
        });
        
        const result = await response.json();
        
        if (result.cover_letter) {
            resultsDiv.innerHTML = `
                <div class="card animate-fade-in">
                    <div class="card-header bg-gradient-info text-white">
                        <h4><i class="fas fa-envelope pulse"></i> Generated Cover Letter</h4>
                    </div>
                    <div class="card-body">
                        <div class="mb-3 animate-slide-in">
                            <div class="d-flex flex-wrap gap-2">
                                <span class="badge bg-primary">Company: ${companyName}</span>
                                <span class="badge bg-success">Position: ${position}</span>
                                <span class="badge bg-info">Tone: ${tone}</span>
                            </div>
                        </div>
                        <div class="position-relative">
                            <textarea class="form-control mb-3 animate-slide-in" rows="20" readonly>${result.cover_letter}</textarea>
                            <div class="typing-indicator" style="display: none;"></div>
                        </div>
                        <div class="d-grid gap-2 animate-slide-in">
                            <button class="btn btn-primary btn-hover-effect" onclick="downloadCoverLetter('${companyName}', \`${result.cover_letter.replace(/`/g, '\\`')}\`)">
                                <i class="fas fa-download"></i> Download Cover Letter
                            </button>
                            <button class="btn btn-outline-secondary btn-hover-effect" onclick="copyToClipboard(\`${result.cover_letter.replace(/`/g, '\\`')}\`)">
                                <i class="fas fa-copy"></i> Copy to Clipboard
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            // Simulate typing effect for the textarea
            setTimeout(() => {
                simulateTyping(resultsDiv.querySelector('textarea'), result.cover_letter);
            }, 500);
            
        } else {
            showAlert('Error: ' + (result.error || 'Unknown error'), 'danger');
            resultsDiv.innerHTML = '';
        }
    } catch (error) {
        showAlert('Cover letter generation failed: ' + error.message, 'danger');
        resultsDiv.innerHTML = '';
    } finally {
        hideLoading(submitBtn, 'Generate Cover Letter');
    }
});

document.getElementById('jobSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const jobTitle = document.getElementById('jobTitle').value;
    const location = document.getElementById('location').value;
    const experienceLevel = document.getElementById('experienceLevel').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById('jobSearchResults');
    
    if (!jobTitle) {
        showAlert('Please enter a job title', 'warning');
        return;
    }
    
    showLoading(submitBtn, 'Searching Jobs...');
    resultsDiv.innerHTML = getLoadingSpinner('Searching for the best job opportunities...');
    
    try {
        const response = await fetch('/search_jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_title: jobTitle,
                location: location,
                experience_level: experienceLevel
            })
        });
        
        const result = await response.json();
        
        if (result.jobs && result.jobs.length > 0) {
            let jobsHtml = `
                <div class="search-header animate-fade-in">
                    <div class="search-results-title">
                        <h4><i class="fas fa-briefcase text-primary"></i> Found ${result.jobs.length} Job${result.jobs.length > 1 ? 's' : ''}</h4>
                        <div class="search-query">
                            <span class="query-tag"><i class="fas fa-search"></i> ${jobTitle}</span>
                            ${location ? `<span class="location-tag"><i class="fas fa-map-marker-alt"></i> ${location}</span>` : ''}
                            <span class="level-tag"><i class="fas fa-layer-group"></i> ${experienceLevel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </div>
                    </div>
                </div>
            `;
            
            result.jobs.forEach((job, index) => {
                jobsHtml += `
                    <div class="enhanced-job-card animate-slide-in" style="animation-delay: ${index * 0.1}s">
                        <div class="job-card-header">
                            <div class="job-title-section">
                                <h5 class="job-title">${job.title}</h5>
                                <div class="company-info">
                                    <i class="fas fa-building company-icon"></i>
                                    <span class="company-name">${job.company}</span>
                                </div>
                            </div>
                            <div class="job-source-badge">
                                <span class="source-tag">${job.source}</span>
                            </div>
                        </div>
                        
                        <div class="job-meta-info">
                            <div class="meta-item">
                                <i class="fas fa-map-marker-alt meta-icon"></i>
                                <span class="meta-label">Location:</span>
                                <span class="meta-value">${job.location}</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-dollar-sign meta-icon"></i>
                                <span class="meta-label">Salary:</span>
                                <span class="meta-value">${job.salary}</span>
                            </div>
                        </div>
                        
                        <div class="job-description">
                            <p class="description-text">${job.description.substring(0, 200)}...</p>
                        </div>
                        
                        <div class="job-actions-enhanced">
                            <a href="${job.url}" target="_blank" class="primary-action-btn">
                                <i class="fas fa-external-link-alt"></i>
                                <span>View Full Job</span>
                            </a>
                            <button class="secondary-action-btn" onclick="copyJobDetails('${job.title}', '${job.company}', '${job.location}')">
                                <i class="fas fa-copy"></i>
                                <span>Copy Details</span>
                            </button>
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = jobsHtml;
        } else {
            resultsDiv.innerHTML = `
                <div class="empty-state enhanced-empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-search-minus"></i>
                    </div>
                    <h4 class="empty-title">No Jobs Found</h4>
                    <p class="empty-description">We couldn't find any jobs matching your criteria.</p>
                    <div class="empty-suggestions">
                        <h6>Try these suggestions:</h6>
                        <ul class="suggestion-list">
                            <li><i class="fas fa-lightbulb"></i> Use broader search terms</li>
                            <li><i class="fas fa-map"></i> Expand your location search</li>
                            <li><i class="fas fa-clock"></i> Check back later for new postings</li>
                        </ul>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        showAlert('Job search failed: ' + error.message, 'danger');
        resultsDiv.innerHTML = '';
    } finally {
        hideLoading(submitBtn, 'Find Jobs');
    }
});

// Enhanced Helper Functions with Visual Effects
function showLoading(button, text) {
    button.disabled = true;
    button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    button.style.opacity = '0.7';
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show animate-slide-down`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function getLoadingSpinner(message) {
    return `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted">${message}</p>
        </div>
    `;
}

function animateProgressBar(progressBar) {
    if (!progressBar) return;
    const targetWidth = progressBar.dataset.width;
    progressBar.style.width = targetWidth;
}

function animateCountUp(element) {
    if (!element) return;
    const target = parseInt(element.dataset.target);
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + '%';
    }, 30);
}

function simulateTyping(textarea, text) {
    textarea.value = '';
    let i = 0;
    const timer = setInterval(() => {
        textarea.value += text.charAt(i);
        i++;
        if (i >= text.length) {
            clearInterval(timer);
        }
        textarea.scrollTop = textarea.scrollHeight;
    }, 10);
}

function downloadCoverLetter(companyName, content) {
    const element = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `cover_letter_${companyName.replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    showAlert('Cover letter downloaded successfully!', 'success');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Cover letter copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

function copyJobDetails(title, company, location) {
    const details = `Job Title: ${title}\nCompany: ${company}\nLocation: ${location}`;
    navigator.clipboard.writeText(details).then(() => {
        showAlert('Job details copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy job details', 'danger');
    });
}

// Tab Navigation Functionality
function initTabNavigation() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Remove active class from all tabs and contents
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// Initialize animations on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab navigation
    initTabNavigation();
    
    // Add hover effects to buttons
    document.querySelectorAll('.btn, .ai-button').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Add file input animation
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const uploadZone = this.closest('.upload-zone');
            if (uploadZone && this.files.length > 0) {
                const fileName = this.files[0].name;
                const fileInfo = uploadZone.querySelector('p');
                if (fileInfo) {
                    fileInfo.innerHTML = `<strong>${fileName}</strong><br><span>File selected successfully</span>`;
                    uploadZone.style.borderColor = '#00ff88';
                    uploadZone.style.background = 'rgba(0, 255, 136, 0.1)';
                }
            }
        });
    });
});