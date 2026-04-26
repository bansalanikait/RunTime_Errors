/**
 * DECEPTRA Dashboard — Session Detail Page
 * Fetches full request chain and renders timeline.
 */

document.addEventListener('DOMContentLoaded', async () => {
    const sessionId = document.getElementById('session-data')?.dataset.sessionId;
    if (!sessionId) return;

    const headerCard = document.getElementById('session-header');
    const timelineContainer = document.getElementById('request-timeline');

    // Show loading
    if (headerCard) DeceptraUI.showLoading(headerCard, 1, 'card');
    if (timelineContainer) DeceptraUI.showLoading(timelineContainer, 6, 'row');

    try {
        const data = await DeceptraAPI.fetch(`/api/attacks/${sessionId}`);
        const session = data.session;
        const requests = data.requests || [];

        // Render session header
        if (headerCard) {
            headerCard.innerHTML = `
                <h3>Session Details</h3>
                <div class="detail-grid fade-in">
                    <div class="detail-item">
                        <span class="label">IP Address</span>
                        <span class="value ip-address">${DeceptraUI.escapeHtml(session.ip_address)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">First Seen</span>
                        <span class="value">${DeceptraUI.formatFullDate(session.first_request_at)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Last Seen</span>
                        <span class="value">${DeceptraUI.formatFullDate(session.last_request_at)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Total Requests</span>
                        <span class="value">${session.request_count}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Type</span>
                        <span class="value">${DeceptraUI.automatedBadge(session.is_automated)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Tags</span>
                        <span class="value">${DeceptraUI.tagBadges(session.tags)}</span>
                    </div>
                </div>`;
        }

        // Render request timeline
        if (timelineContainer) {
            if (requests.length === 0) {
                DeceptraUI.showEmpty(timelineContainer, 'No requests recorded for this session');
                return;
            }

            timelineContainer.innerHTML = `<div class="timeline fade-in">
                ${requests.map((r, i) => `
                    <div class="timeline-item ${r.is_trap_hit ? 'trap-hit' : ''}" onclick="toggleDetail(${i})">
                        <div class="timeline-row">
                            ${DeceptraUI.methodBadge(r.method)}
                            <span class="timeline-path">${DeceptraUI.escapeHtml(r.path)}</span>
                            ${DeceptraUI.statusBadge(r.response_status)}
                            ${r.is_trap_hit ? '<span class="badge badge-trap">🪤 TRAP</span>' : ''}
                        </div>
                        <div class="timeline-meta">
                            <span>🕐 ${DeceptraUI.formatFullDate(r.timestamp)}</span>
                            <span>⏱ ${DeceptraUI.formatDuration(r.duration_ms)}</span>
                            ${r.query_string ? `<span>❓ ${DeceptraUI.escapeHtml(r.query_string)}</span>` : ''}
                        </div>
                        <div class="timeline-detail" id="detail-${i}">
                            <pre>${JSON.stringify({
                                id: r.id,
                                session_id: r.session_id,
                                method: r.method,
                                path: r.path,
                                query_string: r.query_string,
                                response_status: r.response_status,
                                duration_ms: r.duration_ms,
                                is_trap_hit: r.is_trap_hit
                            }, null, 2)}</pre>
                        </div>
                    </div>`).join('')}
            </div>`;
        }

    } catch (err) {
        if (headerCard) DeceptraUI.showError(headerCard, err.message);
        if (timelineContainer) DeceptraUI.showError(timelineContainer, 'Failed to load request chain');
    }
});

/**
 * Toggle expanded detail for a timeline item.
 * @param {number} index
 */
function toggleDetail(index) {
    const el = document.getElementById(`detail-${index}`);
    if (el) el.classList.toggle('show');
}
