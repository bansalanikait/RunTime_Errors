/**
 * DECEPTRA Dashboard — Sessions List Page
 * Full sessions table with client-side filtering and pagination.
 */

(function () {
    const PAGE_SIZE = 25;
    let currentOffset = 0;
    let totalCount = 0;
    let allSessions = []; // Cached for client-side filtering

    const tableBody = document.getElementById('sessions-table-body');
    const tableContainer = document.getElementById('sessions-table-container');
    const paginationInfo = document.getElementById('pagination-info');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const filterIP = document.getElementById('filter-ip');
    const filterTag = document.getElementById('filter-tag');
    const filterType = document.getElementById('filter-type');

    async function loadSessions() {
        if (!tableBody) return;
        DeceptraUI.showLoading(tableBody, 8, 'row');

        try {
            const data = await DeceptraAPI.fetch(
                `/api/attacks?limit=${PAGE_SIZE}&offset=${currentOffset}`
            );
            totalCount = data.total || 0;
            allSessions = data.attacks || [];
            renderTable(allSessions);
            updatePagination();
        } catch (err) {
            DeceptraUI.showError(tableContainer, err.message);
        }
    }

    function renderTable(sessions) {
        if (sessions.length === 0) {
            DeceptraUI.showEmpty(tableContainer, 'No sessions match your filters');
            return;
        }

        // Restore table structure if it was replaced by empty/error state
        if (!document.getElementById('sessions-table-body')) {
            tableContainer.innerHTML = document.getElementById('table-template').innerHTML;
        }

        const body = document.getElementById('sessions-table-body');
        body.innerHTML = sessions.map(s => `
            <tr class="fade-in" onclick="window.location.href='/dashboard/sessions/${s.id}'">
                <td><span class="ip-address">${DeceptraUI.escapeHtml(s.ip_address)}</span></td>
                <td>${DeceptraUI.formatDate(s.first_request_at)}</td>
                <td>${DeceptraUI.formatDate(s.last_request_at)}</td>
                <td><span class="mono">${s.request_count}</span></td>
                <td>${DeceptraUI.automatedBadge(s.is_automated)}</td>
                <td>${DeceptraUI.tagBadges(s.tags)}</td>
                <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${DeceptraUI.escapeHtml(s.user_agent || '')}">${DeceptraUI.escapeHtml(s.user_agent || 'Unknown')}</td>
            </tr>`).join('');
    }

    function updatePagination() {
        if (paginationInfo) {
            const start = totalCount === 0 ? 0 : currentOffset + 1;
            const end = Math.min(currentOffset + PAGE_SIZE, totalCount);
            paginationInfo.textContent = `Showing ${start}–${end} of ${totalCount}`;
        }
        if (btnPrev) btnPrev.disabled = currentOffset === 0;
        if (btnNext) btnNext.disabled = currentOffset + PAGE_SIZE >= totalCount;
    }

    function applyFilters() {
        let filtered = [...allSessions];

        // IP filter
        const ipQuery = (filterIP?.value || '').trim().toLowerCase();
        if (ipQuery) {
            filtered = filtered.filter(s =>
                s.ip_address.toLowerCase().includes(ipQuery)
            );
        }

        // Tag filter
        const tagQuery = (filterTag?.value || '').trim().toLowerCase();
        if (tagQuery) {
            filtered = filtered.filter(s =>
                s.tags && s.tags.toLowerCase().includes(tagQuery)
            );
        }

        // Automated filter
        const typeVal = filterType?.value || 'all';
        if (typeVal === 'automated') {
            filtered = filtered.filter(s => s.is_automated);
        } else if (typeVal === 'manual') {
            filtered = filtered.filter(s => !s.is_automated);
        }

        renderTable(filtered);
    }

    // Event listeners
    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            currentOffset = Math.max(0, currentOffset - PAGE_SIZE);
            loadSessions();
        });
    }

    if (btnNext) {
        btnNext.addEventListener('click', () => {
            if (currentOffset + PAGE_SIZE < totalCount) {
                currentOffset += PAGE_SIZE;
                loadSessions();
            }
        });
    }

    if (filterIP) filterIP.addEventListener('input', applyFilters);
    if (filterTag) filterTag.addEventListener('input', applyFilters);
    if (filterType) filterType.addEventListener('change', applyFilters);

    // Initial load
    document.addEventListener('DOMContentLoaded', loadSessions);
})();
