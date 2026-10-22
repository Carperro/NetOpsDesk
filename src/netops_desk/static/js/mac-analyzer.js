"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("mac-form");
    if (!form) return;

    const macInput = document.getElementById("mac-input");
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
        header.textContent = code || (type === 'error' ? 'Error' : 'Aviso');
        const msg = document.createElement('div');
        msg.className = 'alert__message';
        msg.textContent = message;
        alertDiv.appendChild(header);
        alertDiv.appendChild(msg);
        container.appendChild(alertDiv);
        container.hidden = false;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorArea.hidden = true;
        resultContainer.hidden = true;

        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Analizando...";
        executeBtn.disabled = true;

        try {
            const res = await fetch("/api/v1/tools/mac-analyzer/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mac: macInput.value.trim() })
            });
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            renderResult(data);
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            executeBtn.disabled = false;
            executeBtn.textContent = originalText;
        }
    });

    function renderResult(data) {
        document.getElementById("result-original").textContent = data.mac_original;
        document.getElementById("result-normalized").textContent = data.mac_normalized;
        document.getElementById("result-vendor").textContent = data.vendor;
        resultContainer.hidden = false;
    }
});