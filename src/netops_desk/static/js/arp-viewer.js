"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const executeBtn = document.getElementById("execute-btn");
    if (!executeBtn) return;

    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const tbody = document.getElementById("arp-tbody");

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
        executeBtn.textContent = "Escaneando...";
        executeBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/tools/arp-viewer/execute", { method: "GET" }).catch(() => null);

            if (!response) {
                showAlert(errorArea, 'No se pudo conectar con el servidor.', 'error', 'Sin conexión');
                return;
            }

            const data = await response.json().catch(() => null);
            
            if (!response.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(response, data), 'error', NetOpsApiErrors.title(response));
                return;
            }

            renderResult(data);
        } catch {
            showAlert(errorArea, 'Error inesperado al procesar la solicitud.', 'error', 'Error de cliente');
        } finally {
            executeBtn.disabled = false;
            executeBtn.textContent = originalText;
        }
    });

    function renderResult(data) {
        if (!data.entries || data.entries.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 4;
            td.textContent = "No se encontraron entradas en la caché ARP.";
            td.style.textAlign = "center";
            td.style.color = "var(--text-muted)";
            tr.appendChild(td);
            tbody.appendChild(tr);
        } else {
            data.entries.forEach(entry => {
                const tr = document.createElement("tr");
                
                const fields = [
                    entry.interface_ip, 
                    entry.ip_address, 
                    entry.mac_address, 
                    entry.entry_type === "dynamic" ? "Dinámico" : "Estático"
                ];

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