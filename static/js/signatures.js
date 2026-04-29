/**
 * DECEPTRA Dashboard — Threat Signatures Management (Dev A)
 * NOTE: Backend API (/api/signatures) is pending implementation by Dev C.
 * Currently displaying mock data.
 */

(function () {
    const tableBody = document.getElementById('signatures-table-body');

    async function loadSignatures() {
        if (!tableBody) return;
        
        try {
            // TODO: Replace with real DeceptraAPI.fetch('/api/signatures') once Dev C finishes backend
            console.log("Fetching mock signatures pending Dev C backend implementation...");
            
            // Mock data representing what the backend API contract should look like
            const mockData = [
                { id: 1, name: "SQLi Basic", pattern_regex: "(' OR 1=1|UNION SELECT)", severity: "high", is_active: true },
                { id: 2, name: "XSS Basic", pattern_regex: "(<script>|javascript:)", severity: "high", is_active: true },
                { id: 3, name: "Recon Probe", pattern_regex: "(\\.env|\\.git|wp-config)", severity: "medium", is_active: true },
                { id: 4, name: "Path Traversal", pattern_regex: "(\\.\\./|\\.\\.\\\\)", severity: "high", is_active: true }
            ];
            
            // Simulate network delay
            await new Promise(r => setTimeout(r, 500));
            
            tableBody.innerHTML = mockData.map(s => `
                <tr class="fade-in">
                    <td style="font-weight: bold; color: #fff;">${DeceptraUI.escapeHtml(s.name)}</td>
                    <td class="mono" style="color: #ffcc00; letter-spacing: 1px;">${DeceptraUI.escapeHtml(s.pattern_regex)}</td>
                    <td><span class="badge" style="background: rgba(255, 68, 68, 0.2); color: #ff4444;">${DeceptraUI.escapeHtml(s.severity.toUpperCase())}</span></td>
                    <td><span class="badge badge-trap">Active</span></td>
                </tr>
            `).join('');
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="4" style="color: #ff4444; text-align: center;">Failed to load signatures: ${err.message}</td></tr>`;
        }
    }

    // Initial load
    document.addEventListener('DOMContentLoaded', loadSignatures);
})();
