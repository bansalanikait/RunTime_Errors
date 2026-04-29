/**
 * DECEPTRA Dashboard — Decoys Management
 */

(function () {
    const tableBody = document.getElementById('decoys-table-body');
    const btnCreate = document.getElementById('btn-create-decoy');
    const pathInput = document.getElementById('new-decoy-path');
    const typeInput = document.getElementById('new-decoy-type');
    const statusText = document.getElementById('decoy-create-status');

    async function loadDecoys() {
        if (!tableBody) return;
        
        try {
            const data = await DeceptraAPI.fetch('/api/decoys');
            const decoys = data.decoys || [];
            
            if (decoys.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #888;">No active decoys found.</td></tr>';
                return;
            }

            tableBody.innerHTML = decoys.map(d => `
                <tr class="fade-in">
                    <td class="mono" style="color: #00d2ff;">${DeceptraUI.escapeHtml(d.path)}</td>
                    <td><span class="badge" style="background: rgba(255, 255, 255, 0.1);">${DeceptraUI.escapeHtml(d.response_type)}</span></td>
                    <td><span class="badge badge-trap">Active</span></td>
                </tr>
            `).join('');
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="3" style="color: #ff4444; text-align: center;">Failed to load decoys: ${err.message}</td></tr>`;
        }
    }

    async function createDecoy() {
        const path = pathInput.value.trim();
        const type = typeInput.value;

        if (!path || !path.startsWith('/')) {
            statusText.textContent = "Error: Path must start with '/'";
            statusText.style.color = "#ff4444";
            return;
        }

        btnCreate.disabled = true;
        btnCreate.textContent = "Deploying...";
        statusText.textContent = "";

        try {
            await DeceptraAPI.fetch('/api/decoys', {
                method: 'POST',
                body: JSON.stringify({ path: path, response_type: type })
            });

            pathInput.value = '';
            statusText.textContent = "✅ Decoy successfully deployed!";
            statusText.style.color = "#44ff44";
            
            // Reload the table
            await loadDecoys();
        } catch (err) {
            statusText.textContent = `❌ Failed to create decoy: ${err.message}`;
            statusText.style.color = "#ff4444";
        } finally {
            btnCreate.disabled = false;
            btnCreate.textContent = "➕ Deploy Decoy";
        }
    }

    if (btnCreate) {
        btnCreate.addEventListener('click', createDecoy);
    }

    // Initial load
    document.addEventListener('DOMContentLoaded', loadDecoys);
})();
