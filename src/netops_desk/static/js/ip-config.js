"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("ipconfig-form");
    if (!form) return;

    const actionInput = document.getElementById("action-input");
    const staticFields = document.getElementById("static-fields");
    const dnsFields = document.getElementById("dns-fields");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const copyBtn = document.getElementById("copy-btn");
    const submitBtn = form.querySelector('button[type="submit"]');

    // Mostrar/ocultar campos según la acción
    actionInput.addEventListener("change", () => {
        const action = actionInput.value;
        staticFields.hidden = (action !== "set_static");
        dnsFields.hidden = (action !== "set_dns");
        resultContainer.hidden = true;
        errorArea.hidden = true;
    });

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
        errorArea.hidden = true;
        resultContainer.hidden = true;
        const idleLabel = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Generando...";
            submitBtn.setAttribute("aria-busy", "true");
        }

        const payload = {
            action: actionInput.value,
            interface_name: document.getElementById("iface-input").value.trim(),
            ip: document.getElementById("ip-input").value.trim() || null,
            mask: document.getElementById("mask-input").value.trim() || null,
            gateway: document.getElementById("gw-input").value.trim() || null,
            dns_ip: document.getElementById("dns-input").value.trim() || null
        };

        try {
            const response = await fetch("/api/v1/tools/ip-config/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }).catch(() => null);

            if (!response) return showAlert(errorArea, 'Error de conexión.', 'error', 'Sin red');
            
            const data = await response.json().catch(() => null);
            
            if (!response.ok) {
                return showAlert(errorArea, NetOpsApiErrors.message(response, data), 'error', NetOpsApiErrors.title(response));
            }

            document.getElementById("result-command").textContent = data.command;
            document.getElementById("result-explanation").textContent = data.explanation;
            resultContainer.hidden = false;

        } catch {
            showAlert(errorArea, 'Error inesperado.', 'error', 'Error de cliente');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = idleLabel;
                submitBtn.removeAttribute("aria-busy");
            }
        }
    });

    copyBtn.addEventListener("click", async () => {
        const text = document.getElementById("result-command").textContent;
        try {
            await navigator.clipboard.writeText(text);
            const original = copyBtn.textContent;
            copyBtn.textContent = "¡Copiado!";
            setTimeout(() => copyBtn.textContent = original, 2000);
        } catch {
            showAlert(errorArea, 'No se pudo copiar al portapapeles.', 'error');
        }
    });
});
