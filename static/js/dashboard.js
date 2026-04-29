/**
 * DECEPTRA Dashboard — Shared Utilities
 * API wrapper, UI helpers, formatters
 */

const DeceptraAPI = {
    /**
     * Fetch JSON from API with error handling.
     * @param {string} url - API endpoint
     * @returns {Promise<Object>} Parsed JSON
     */
    async fetch(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`[DeceptraAPI] Fetch failed: ${url}`, error);
            throw error;
        }
    }
};

const DeceptraUI = {
    /**
     * Show loading skeletons in container.
     * @param {HTMLElement} container
     * @param {number} count - Number of skeleton rows
     * @param {string} type - 'stat'|'row'|'card'
     */
    showLoading(container, count = 4, type = 'row') {
        const cls = `skeleton skeleton-${type}`;
        let html = '';
        for (let i = 0; i < count; i++) {
            html += `<div class="${cls}"></div>`;
        }
        container.innerHTML = html;
    },

    /** Hide loading by clearing container. */
    hideLoading(container) {
        container.innerHTML = '';
    },

    /**
     * Show empty state.
     * @param {HTMLElement} container
     * @param {string} message
     */
    showEmpty(container, message = 'No data yet') {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <h4>${message}</h4>
                <p>Data will appear here once the honeypot captures traffic.</p>
            </div>`;
    },

    /**
     * Show error state.
     * @param {HTMLElement} container
     * @param {string} message
     */
    showError(container, message = 'Failed to load data') {
        container.innerHTML = `
            <div class="error-state">
                <div class="icon">⚠️</div>
                <h4>Error</h4>
                <p>${message}</p>
            </div>`;
    },

    /**
     * Format ISO date string to readable format.
     * @param {string} isoString
     * @returns {string}
     */
    formatDate(isoString) {
        if (!isoString) return '—';
        const d = new Date(isoString);
        const now = new Date();
        const diffMs = now - d;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;

        return d.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: false
        });
    },

    /**
     * Format full date.
     * @param {string} isoString
     * @returns {string}
     */
    formatFullDate(isoString) {
        if (!isoString) return '—';
        return new Date(isoString).toLocaleString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        });
    },

    /**
     * Format duration in ms to human string.
     * @param {number} ms
     * @returns {string}
     */
    formatDuration(ms) {
        if (ms == null) return '—';
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    },

    /**
     * Get method badge HTML.
     * @param {string} method
     * @returns {string}
     */
    methodBadge(method) {
        const m = (method || 'GET').toUpperCase();
        return `<span class="badge badge-${m.toLowerCase()}">${m}</span>`;
    },

    /**
     * Get status code badge HTML.
     * @param {number} status
     * @returns {string}
     */
    statusBadge(status) {
        if (!status) return '';
        let cls = 'badge-2xx';
        if (status >= 300 && status < 400) cls = 'badge-3xx';
        else if (status >= 400 && status < 500) cls = 'badge-4xx';
        else if (status >= 500) cls = 'badge-5xx';
        return `<span class="badge ${cls}">${status}</span>`;
    },

    /**
     * Render tag badges from comma-separated string.
     * @param {string|null} tags
     * @returns {string}
     */
    tagBadges(tags) {
        if (!tags) return '<span style="color:var(--text-muted)">—</span>';
        return tags.split(',').map(t => t.trim()).filter(Boolean)
            .map(t => `<span class="badge badge-tag">${t}</span>`).join('');
    },

    /**
     * Render automated badge.
     * @param {boolean} isAutomated
     * @returns {string}
     */
    automatedBadge(isAutomated) {
        if (isAutomated) return '<span class="badge badge-automated">🤖 Bot</span>';
        return '<span class="badge badge-manual">👤 Manual</span>';
    },

    /**
     * Escape HTML to prevent XSS.
     * @param {string} str
     * @returns {string}
     */
    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};

/**
 * Check backend health and update sidebar indicator.
 */
async function checkHealth() {
    const dot = document.getElementById('health-dot');
    const label = document.getElementById('health-label');
    if (!dot || !label) return;

    try {
        const data = await DeceptraAPI.fetch('/api/health');
        if (data.status === 'ok') {
            dot.className = 'health-dot online';
            label.textContent = `Online · v${data.version}`;
        } else {
            dot.className = 'health-dot offline';
            label.textContent = 'Unhealthy';
        }
    } catch {
        dot.className = 'health-dot offline';
        label.textContent = 'Offline';
    }
}

// Run health check on every page
document.addEventListener('DOMContentLoaded', checkHealth);
