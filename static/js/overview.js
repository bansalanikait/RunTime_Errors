/**
 * DECEPTRA Dashboard — Overview Page
 * Fetches stats and recent sessions from /api/attacks
 */

document.addEventListener('DOMContentLoaded', async () => {
    const statsGrid = document.getElementById('stats-grid');
    const recentBody = document.getElementById('recent-sessions-body');
    const recentContainer = document.getElementById('recent-sessions-container');

    // Show loading
    if (statsGrid) DeceptraUI.showLoading(statsGrid, 4, 'stat');
    if (recentBody) DeceptraUI.showLoading(recentBody, 5, 'row');

    try {
        const data = await DeceptraAPI.fetch('/api/attacks?limit=100&offset=0');
        const attacks = data.attacks || [];

        // Compute stats
        const totalSessions = data.total || attacks.length;
        const totalRequests = attacks.reduce((sum, a) => sum + (a.request_count || 0), 0);
        const uniqueIPs = new Set(attacks.map(a => a.ip_address)).size;
        const automatedCount = attacks.filter(a => a.is_automated).length;

        // Render stat cards
        if (statsGrid) {
            statsGrid.innerHTML = `
                <div class="stat-card accent fade-in">
                    <div class="stat-icon">📡</div>
                    <div class="stat-value">${totalSessions}</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                <div class="stat-card info fade-in">
                    <div class="stat-icon">📨</div>
                    <div class="stat-value">${totalRequests}</div>
                    <div class="stat-label">Total Requests</div>
                </div>
                <div class="stat-card warning fade-in">
                    <div class="stat-icon">🌐</div>
                    <div class="stat-value">${uniqueIPs}</div>
                    <div class="stat-label">Unique IPs</div>
                </div>
                <div class="stat-card danger fade-in">
                    <div class="stat-icon">🤖</div>
                    <div class="stat-value">${automatedCount}</div>
                    <div class="stat-label">Automated Attacks</div>
                </div>`;
        }

        // Render recent sessions (last 10)
        if (recentBody) {
            const recent = attacks.slice(0, 10);
            if (recent.length === 0) {
                DeceptraUI.showEmpty(recentContainer, 'No sessions captured yet');
                return;
            }

            recentBody.innerHTML = recent.map(s => `
                <tr class="fade-in" onclick="window.location.href='/dashboard/sessions/${s.id}'">
                    <td><span class="ip-address">${DeceptraUI.escapeHtml(s.ip_address)}</span></td>
                    <td>${DeceptraUI.formatDate(s.last_request_at)}</td>
                    <td><span class="mono">${s.request_count}</span></td>
                    <td>${DeceptraUI.automatedBadge(s.is_automated)}</td>
                    <td>${DeceptraUI.tagBadges(s.tags)}</td>
                </tr>`).join('');
        }

    } catch (err) {
        if (statsGrid) DeceptraUI.showError(statsGrid, 'Failed to load statistics');
        if (recentContainer) DeceptraUI.showError(recentContainer, err.message);
    }
});
