/**
 * DECEPTRA Dashboard — Threat Signatures Management (Dev A)
 * Fetches dynamic rules from Dev C's backend API.
 */

(function () {
    const tableBody = document.getElementById('signatures-table-body');
    const btnAdd = document.getElementById('btn-add-sig');
    const nameInput = document.getElementById('new-sig-name');
    const patternInput = document.getElementById('new-sig-pattern');
    const targetInput = document.getElementById('new-sig-target');
    const severityInput = document.getElementById('new-sig-severity');
    const typeInput = document.getElementById('new-sig-type');
    const statusText = document.getElementById('sig-create-status');

    async function loadSignatures() {
        if (!tableBody) return;
        
        try {
            const data = await DeceptraAPI.fetch('/api/signatures');
            const signatures = Array.isArray(data) ? data : (data.signatures || []);
            
            if (signatures.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #888;">No active signatures found.</td></tr>';
                return;
            }
            
            tableBody.innerHTML = signatures.map(s => `
                <tr class="fade-in">
                    <td style="font-weight: bold; color: #fff;">${DeceptraUI.escapeHtml(s.name)}</td>
                    <td class="mono" style="color: #ffcc00; letter-spacing: 1px;">${DeceptraUI.escapeHtml(s.pattern)}</td>
                    <td><span class="badge" style="background: rgba(255, 68, 68, 0.2); color: #ff4444;">${DeceptraUI.escapeHtml(s.threat_tag)}</span></td>
                    <td><span class="badge badge-trap">Active</span></td>
                </tr>
            `).join('');
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="4" style="color: #ff4444; text-align: center;">Failed to load signatures: ${err.message}</td></tr>`;
        }
    }

    async function createSignature() {
        const name = nameInput.value.trim();
        const pattern = patternInput.value.trim();
        const target = targetInput.value.trim();
        const severity = severityInput.value;
        const type = typeInput.value.trim();

        if (!name || !pattern || !target || !type) {
            statusText.textContent = "Error: All fields are required.";
            statusText.style.color = "#ff4444";
            return;
        }

        btnAdd.disabled = true;
        btnAdd.textContent = "Adding...";
        statusText.textContent = "";

        try {
            await DeceptraAPI.fetch('/api/signatures', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    name: name, 
                    pattern: pattern,
                    target: target,
                    threat_tag: type,
                    is_active: true
                })
            });

            nameInput.value = '';
            patternInput.value = '';
            targetInput.value = '';
            typeInput.value = '';
            
            statusText.textContent = "✅ Signature successfully added and cached!";
            statusText.style.color = "#44ff44";
            
            // Reload the table
            await loadSignatures();
        } catch (err) {
            statusText.textContent = `❌ Failed to add signature: ${err.message}`;
            statusText.style.color = "#ff4444";
        } finally {
            btnAdd.disabled = false;
            btnAdd.textContent = "➕ Add Rule";
        }
    }

    if (btnAdd) {
        btnAdd.addEventListener('click', createSignature);
    }

    // Initial load
    document.addEventListener('DOMContentLoaded', loadSignatures);
})();
