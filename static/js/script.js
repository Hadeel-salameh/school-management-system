/* ================================================================
   SCHOOL MANAGEMENT SYSTEM - MAIN JAVASCRIPT
   ================================================================ */

'use strict';

// ── Sidebar Toggle ──────────────────────────────────────────────────────────

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const openBtn = document.getElementById('openSidebar');
    const closeBtn = document.getElementById('sidebarToggle');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (overlay) overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    if (openBtn) openBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSidebar();
    });
}

// ── Active Sidebar Link ─────────────────────────────────────────────────────

function setActiveSidebarLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// ── Confirm Delete ──────────────────────────────────────────────────────────

function initConfirmDelete() {
    document.querySelectorAll('.btn-delete, [data-confirm]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = btn.dataset.confirm || 'هل أنت متأكد من أنك تريد حذف هذا العنصر؟ لا يمكن التراجع عن هذا الإجراء.';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// ── Auto Dismiss Alerts ─────────────────────────────────────────────────────

function initAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            if (alert.classList.contains('show')) {
                bsAlert.close();
            }
        }, 5000);
    });
}

// ── Role Selector on Login ──────────────────────────────────────────────────

function initRoleSelector() {
    const roleBtns = document.querySelectorAll('.role-btn');
    const roleInput = document.getElementById('roleInput');

    roleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            roleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (roleInput) {
                roleInput.value = btn.dataset.role;
            }
        });
    });
}

// ── Navbar Scroll Effect ────────────────────────────────────────────────────

function initNavbarScroll() {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
            navbar.style.height = '60px';
        } else {
            navbar.classList.remove('scrolled');
            navbar.style.height = '';
        }
    }, { passive: true });
}

// ── Animated Counters ────────────────────────────────────────────────────────

function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    const duration = 1500;
    const step = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            el.textContent = target.toLocaleString('ar-EG');
            clearInterval(timer);
        } else {
            el.textContent = Math.floor(current).toLocaleString('ar-EG');
        }
    }, 16);
}

function initCounters() {
    const counters = document.querySelectorAll('.counter-animate');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counter.dataset.target = counter.textContent;
        observer.observe(counter);
    });
}

// ── Grade Distribution Chart ─────────────────────────────────────────────────

function initGradeChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#10b981',
                    '#1a56db',
                    '#06b6d4',
                    '#f59e0b',
                    '#ef4444',
                ],
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: 'Cairo', size: 12 },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 8
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// ── Attendance Line Chart ────────────────────────────────────────────────────

function initAttendanceChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, 'rgba(26,86,219,.3)');
    gradient.addColorStop(1, 'rgba(26,86,219,0)');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'نسبة الحضور %',
                data: data,
                borderColor: '#1a56db',
                backgroundColor: gradient,
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#1a56db',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 50,
                    max: 100,
                    grid: { color: '#f3f4f6', drawBorder: false },
                    ticks: { font: { family: 'Cairo', size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Cairo', size: 11 } }
                }
            }
        }
    });
}

// ── Bar Chart ────────────────────────────────────────────────────────────────

function initBarChart(canvasId, labels, data, color = '#1a56db') {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;

    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'الدرجات',
                data: data,
                backgroundColor: color,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: '#f3f4f6' },
                    ticks: { font: { family: 'Cairo', size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Cairo', size: 11 } }
                }
            }
        }
    });
}

// ── Tooltip Init ─────────────────────────────────────────────────────────────

function initTooltips() {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));
}

// ── Search Table ─────────────────────────────────────────────────────────────

function initTableSearch() {
    const searchInput = document.getElementById('tableSearch');
    const tableBody = document.querySelector('#searchableTable tbody');
    if (!searchInput || !tableBody) return;

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        tableBody.querySelectorAll('tr').forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}

// ── Print Report ─────────────────────────────────────────────────────────────

function printReport() {
    window.print();
}

// ── Theme / Dark mode (future) ───────────────────────────────────────────────

// ── Floating Action Label ────────────────────────────────────────────────────

function initFormFloat() {
    document.querySelectorAll('.input-group input, .input-group select').forEach(input => {
        input.addEventListener('focus', () => {
            input.closest('.input-group')?.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            input.closest('.input-group')?.classList.remove('focused');
        });
    });
}

// ── Init All ─────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    setActiveSidebarLink();
    initConfirmDelete();
    initAlerts();
    initRoleSelector();
    initNavbarScroll();
    initCounters();
    initTooltips();
    initTableSearch();
    initFormFloat();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
});
