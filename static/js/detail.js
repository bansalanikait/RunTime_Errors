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
                        <span class="label">User-Agent</span>
                        <span class="value" style="font-family: monospace; font-size: 0.85em; word-break: break-all;">${DeceptraUI.escapeHtml(session.user_agent || 'Unknown')}</span>
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
                            <div class="raw-data-section">
                                <strong>Request Details:</strong>
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
                                
                                ${r.headers_json ? `
                                <strong style="margin-top: 10px; display: block; color: #ffcc00;">Raw Headers:</strong>
                                <pre style="border-left: 3px solid #ffcc00;">${DeceptraUI.escapeHtml(r.headers_json)}</pre>
                                ` : ''}

                                ${r.body ? `
                                <strong style="margin-top: 10px; display: block; color: #ff4444;">Request Body (Payload):</strong>
                                <pre style="border-left: 3px solid #ff4444;">${DeceptraUI.escapeHtml(r.body)}</pre>
                                ` : ''}

                                ${r.response_body ? `
                                <strong style="margin-top: 10px; display: block; color: #00d2ff;">Response Body:</strong>
                                <pre style="border-left: 3px solid #00d2ff; max-height: 200px; overflow-y: auto;">${DeceptraUI.escapeHtml(r.response_body)}</pre>
                                ` : ''}
                            </div>
                        </div>
                    </div>`).join('')}
            </div>`;
        }

    } catch (err) {
        if (headerCard) DeceptraUI.showError(headerCard, err.message);
        if (timelineContainer) DeceptraUI.showError(timelineContainer, 'Failed to load request chain');
    }

    // AI Summary Logic
    const summaryBtn = document.getElementById('btn-generate-summary');
    const summaryContainer = document.getElementById('ai-summary-container');
    const summaryContent = document.getElementById('ai-summary-content');

    if (summaryBtn) {
        summaryBtn.addEventListener('click', async () => {
            summaryBtn.disabled = true;
            summaryBtn.innerHTML = 'Generating... (Takes ~10s) ⏳';
            summaryContainer.style.display = 'block';
            summaryContent.innerHTML = '<div class="skeleton skeleton-row"></div><div class="skeleton skeleton-row"></div>';

            try {
                const response = await fetch(`/api/attacks/${sessionId}/summary`);
                const data = await response.json();
                
                if (data.headline === "AI Analysis Unavailable") {
                    summaryContent.innerHTML = `
                        <h4 style="color: #ff4444;">⚠️ ${DeceptraUI.escapeHtml(data.headline)}</h4>
                        <p>${DeceptraUI.escapeHtml(data.description)}</p>
                        <p style="color: #aaa;"><i>${DeceptraUI.escapeHtml(data.recommendations[0] || data.recommendations)}</i></p>
                    `;
                } else {
                    summaryContent.innerHTML = `
                        <h4 style="color: #00d2ff; margin-bottom: 10px;">${DeceptraUI.escapeHtml(data.headline)}</h4>
                        <p style="margin-bottom: 15px; line-height: 1.5;">${DeceptraUI.escapeHtml(data.description)}</p>
                        
                        <div style="margin-bottom: 10px;">
                            <strong style="color: #ffcc00;">Detected Techniques:</strong>
                            <div style="margin-top: 5px;">
                                ${data.suspected_techniques.map(t => `<span class="badge" style="background: rgba(255, 204, 0, 0.2); color: #ffcc00; border: 1px solid #ffcc00;">${DeceptraUI.escapeHtml(t)}</span>`).join(' ')}
                            </div>
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <strong style="color: #00d2ff;">Recommendations:</strong>
                            <ul style="margin-top: 5px; padding-left: 20px; color: #ccc;">
                                ${data.recommendations.map(r => `<li>${DeceptraUI.escapeHtml(r)}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            } catch (err) {
                summaryContent.innerHTML = `<p style="color: #ff4444;">Failed to load summary: ${err.message}</p>`;
            } finally {
                summaryBtn.innerHTML = 'Generate AI Summary ✨';
                summaryBtn.disabled = false;
            }
        });
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
