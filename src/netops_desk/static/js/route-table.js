"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const executeBtn = document.getElementById("execute-btn");
    if (!executeBtn) return;

    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const tbody = document.getElementById("routes-tbody");

    function showAlert(container, message, type = 'error', code = '') {
        if (!container) return;
        container.innerHTML = ''; 
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${type}`;
        const header = document.createElement('div');
        header.className = 'alert__header';
        header.textContent = code || (type === 'error' ? 'Error' : 'Advertencia');
        const msg = document.createElement('div');
        msg.className = 'alert__message';
        msg.textContent = message;
        alertDiv.appendChild(header);
        alertDiv.appendChild(msg);
        container.appendChild(alertDiv);
        container.hidden = false;
    }

    executeBtn.addEventListener("click", async () => {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultContainer.hidden = true;
        tbody.innerHTML = '';

        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Consultando...";
        executeBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/tools/route-table/execute", { method: "GET" }).catch(() => null);

            if (!response) return showAlert(errorArea, 'No se pudo conectar con el servidor.', 'error', 'Sin conexión');
            
            const data = await response.json().catch(() => null);
            if (!response.ok) {
                return showAlert(errorArea, NetOpsApiErrors.message(response, data), 'error', NetOpsApiErrors.title(response));
            }

            renderResult(data);

        } catch {
            showAlert(errorArea, 'Error inesperado.', 'error', 'Error de cliente');
        } finally {
            executeBtn.disabled = false;
            executeBtn.textContent = originalText;
        }
    });

    function renderResult(data) {
        if (!data.routes || data.routes.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.textContent = "No se encontraron rutas.";
            td.style.textAlign = "center";
            tr.appendChild(td);
            tbody.appendChild(tr);
        } else {
            data.routes.forEach(r => {
                const tr = document.createElement("tr");
                const fields = [r.destination, r.netmask, r.gateway, r.interface, r.metric];
                fields.forEach(text => {
                    const td = document.createElement("td");
                    td.textContent = text;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }
        resultContainer.hidden = false;
    }
});