"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const executeBtn = document.getElementById("execute-btn");
    if (!executeBtn) return;

    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const tbody = document.getElementById("adapters-tbody");

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
            const response = await fetch("/api/v1/tools/adapters/execute", { method: "GET" }).catch(() => null);

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
        if (!data.adapters || data.adapters.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.textContent = "No se encontraron adaptadores.";
            td.style.textAlign = "center";
            tr.appendChild(td);
            tbody.appendChild(tr);
        } else {
            data.adapters.forEach(a => {
                const tr = document.createElement("tr");
                
                const speedText = a.speed_mbps > 0 ? `${a.speed_mbps} Mbps` : "Desconocida";
                const stateText = a.is_up ? "Activo" : "Desconectado";
                const multicastText = a.is_multicast ? "Sí" : "No";

                const fields = [a.name, stateText, speedText, a.mtu, multicastText];
                
                fields.forEach((text, index) => {
                    const td = document.createElement("td");
                    td.textContent = text;
                    // Pintamos el estado de verde o rojo
                    if (index === 1) {
                        td.style.fontWeight = "bold";
                        td.style.color = a.is_up ? "#10b981" : "#ef4444";
                    }
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }
        resultContainer.hidden = false;
    }
});