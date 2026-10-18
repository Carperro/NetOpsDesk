document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    const form = document.getElementById('overlap-form');
    const resultsContainer = document.getElementById('overlap-results');
    const errorArea = document.getElementById('error-area');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorArea.innerHTML = '';
        resultsContainer.hidden = true;

        const rawInput = document.getElementById('networks-input').value;
        
        // Separar por saltos de línea y quitar espacios en blanco
        const networks = rawInput.split('\n')
            .map(line => line.trim())
            .filter(line => line !== '');

        if (networks.length < 2) {
            return showAlert(errorArea, "Debés ingresar al menos 2 redes para comparar.", 'error', 'DATOS INSUFICIENTES');
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analizando...';

        try {
            const response = await fetch('/api/v1/tools/overlap/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ networks: networks })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error al analizar las redes.');
            }

            renderResults(data);
        } catch (error) {
            showAlert(errorArea, error.message, 'error', 'ERROR DE RED');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    function renderResults(data) {
        const statusBanner = document.getElementById('status-banner');
        const tableContainer = document.getElementById('conflicts-table-container');
        const tbody = document.getElementById('overlap-tbody');
        
        tbody.innerHTML = '';

        if (data.has_overlap) {
            showAlert(statusBanner, "Se encontraron solapamientos. Revisá la tabla.", 'error', 'CONFLICTOS DETECTADOS');
            tableContainer.hidden = false;

            data.overlaps.forEach(conflict => {
                const tr = document.createElement('tr');
                const cells = [
                    conflict.network_a,
                    conflict.network_b,
                    conflict.message
                ];
                cells.forEach(text => {
                    const td = document.createElement('td');
                    td.textContent = text;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        } else {
            showAlert(statusBanner, "Todas las redes son independientes. No hay solapamientos.", 'warning', 'SIN CONFLICTOS');
            tableContainer.hidden = true;
        }

        resultsContainer.hidden = false;
    }

    // Función auxiliar de alertas
    function showAlert(container, message, type = 'error', code = '') {
        if (!container) return;
        container.innerHTML = ''; 
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${type}`;
        alertDiv.innerHTML = `
            <div class="alert__header">${code || 'Error'}</div>
            <div class="alert__message">${message}</div>
        `;
        container.appendChild(alertDiv);
    }
});