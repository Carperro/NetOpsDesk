"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("tcp-form");
    if (!form) return;

    const hostInput = document.getElementById("host-input");
    const portInput = document.getElementById("port-input");
    const timeoutInput = document.getElementById("timeout-input");
    const executeBtn = document.getElementById("execute-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");

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

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitTest();
    });

    async function submitTest() {
        clearOutputs();
        
        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Probando...";
        form.setAttribute("aria-busy", "true");
        executeBtn.disabled = true;

        const payload = {
            host: hostInput.value.trim(),
            port: parseInt(portInput.value, 10),
            timeout_ms: parseInt(timeoutInput.value, 10)
        };

        try {
            const response = await fetch("/api/v1/tools/tcp-test/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
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
            form.removeAttribute("aria-busy");
            executeBtn.disabled = false;
            executeBtn.textContent = originalText;
        }
    }

    function clearOutputs() {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultContainer.hidden = true;
    }

    function renderResult(data) {
        document.getElementById("result-host").textContent = data.host;
        document.getElementById("result-port").textContent = data.port;
        
        const statusEl = document.getElementById("result-status");
        statusEl.textContent = data.status.toUpperCase();
        
        // Colores según el estado
        if (data.status === "open") statusEl.className = "status-open";
        else if (data.status === "closed") statusEl.className = "status-closed";
        else statusEl.className = "status-filtered";

        document.getElementById("result-time").textContent = `${data.time_ms} ms`;

        resultContainer.hidden = false;
    }
});