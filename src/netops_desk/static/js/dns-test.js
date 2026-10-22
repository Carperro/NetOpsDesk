"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("dns-form");
    if (!form) return;

    const domainInput = document.getElementById("domain-input");
    const typeInput = document.getElementById("type-input");
    const resolverInput = document.getElementById("resolver-input");
    const executeBtn = document.getElementById("execute-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const recordsList = document.getElementById("records-list");

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
        await submitDnsTest();
    });

    async function submitDnsTest() {
        clearOutputs();
        
        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Consultando...";
        form.setAttribute("aria-busy", "true");
        executeBtn.disabled = true;

        const payload = {
            domain: domainInput.value.trim(),
            record_type: typeInput.value,
            resolver: resolverInput.value.trim() || null // null si está vacío
        };

        try {
            const response = await fetch("/api/v1/tools/dns-test/execute", {
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
        recordsList.innerHTML = '';
    }

    function renderResult(data) {
        document.getElementById("result-domain").textContent = data.domain;
        document.getElementById("result-type").textContent = data.record_type;
        document.getElementById("result-resolver").textContent = data.resolver;
        document.getElementById("result-time").textContent = `${data.time_ms} ms`;

        if (data.status === "nxdomain") {
            showAlert(errorArea, "El dominio no existe (NXDOMAIN). Verificá si está bien escrito.", "warning", "Dominio no encontrado");
            resultContainer.hidden = true;
            return;
        }

        if (data.records.length === 0) {
            const li = document.createElement("li");
            li.textContent = "El servidor no devolvió registros para este tipo.";
            li.className = "text-muted";
            recordsList.appendChild(li);
        } else {
            data.records.forEach(record => {
                const li = document.createElement("li");
                li.textContent = record;
                recordsList.appendChild(li);
            });
        }

        resultContainer.hidden = false;
    }
});