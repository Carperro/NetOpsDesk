"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const executeBtn = document.getElementById("execute-btn");
    if (!executeBtn) return;

    const errorArea = document.getElementById("error-container");
    const resultWrapper = document.getElementById("result-wrapper");
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
        clearOutputs();
        
        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Analizando...";
        executeBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/tools/route-analyzer/execute", {
                method: "GET"
            }).catch(() => null);

            if (!response) {
                showAlert(errorArea, 'No se pudo conectar con el servidor.', 'error', 'Sin conexión');
                return;
            }

            const data = await response.json().catch(() => null);
            
            if (!response.ok) {
                showAlert(
                    errorArea, 
                    NetOpsApiErrors.message(response, data), 
                    'error', 
                    NetOpsApiErrors.title(response)
                );
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

    function clearOutputs() {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultWrapper.hidden = true;
        tbody.innerHTML = '';
    }

    function renderResult(data) {
        document.getElementById("result-gateway").textContent = data.default_gateway || "No detectado";

        data.routes.forEach(route => {
            const tr = document.createElement("tr");
            
            const fields = [
                route.destination, 
                route.netmask, 
                route.gateway, 
                route.interface, 
                route.metric
            ];

            fields.forEach(text => {
                const td = document.createElement("td");
                td.textContent = text;
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        resultWrapper.hidden = false;
    }
});