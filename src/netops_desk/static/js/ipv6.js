"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("ipv6-form");
    if (!form) return;

    const input = document.getElementById("cidr-input");
    const submitBtn = document.getElementById("calculate-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const warningsContainer = document.getElementById("warnings-container");

    const fields = {
        input: document.getElementById("result-input"),
        address: document.getElementById("result-address"),
        prefix_length: document.getElementById("result-prefix-length"),
        network: document.getElementById("result-network"),
        last_address: document.getElementById("result-last-address"),
        total_addresses: document.getElementById("result-total-addresses"),
        host_bits_set: document.getElementById("result-host-bits-set"),
        classifications: document.getElementById("result-classifications"),
    };

    // --- Función de Alertas Unificada (copiada del contrato visual) ---
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
        await submitCalculation();
    });

    async function submitCalculation() {
        clearOutputs();

        form.setAttribute("aria-busy", "true");
        submitBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/tools/ipv6/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cidr: input.value.trim() }),
            }).catch(() => null);

            if (!response) {
                showAlert(errorArea, 'No se pudo conectar con el servidor. Verificá la conexión e intentá de nuevo.', 'error', 'Sin conexión');
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
            showAlert(errorArea, 'No se pudo procesar la respuesta. Revisá los datos e intentá de nuevo.', 'error', 'Error de cálculo');
        } finally {
            form.removeAttribute("aria-busy");
            submitBtn.disabled = false;
        }
    }

    function clearOutputs() {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultContainer.hidden = true;
        warningsContainer.innerHTML = '';
        warningsContainer.hidden = true;
        
        for (const el of Object.values(fields)) {
            if (el) el.textContent = "—";
        }
    }

    function renderResult(data) {
        for (const [key, el] of Object.entries(fields)) {
            if (!el) continue;
            el.textContent = stringifyValue(data[key]);
        }

        // Renderizado de Advertencias usando el contrato visual
        if (Array.isArray(data.warnings) && data.warnings.length > 0) {
            warningsContainer.innerHTML = '';
            for (const w of data.warnings) {
                // Usamos 'warning' como type y el código como header
                showAlert(warningsContainer, w.message, 'warning', w.code.toUpperCase());
            }
            warningsContainer.hidden = false;
        }

        resultContainer.hidden = false;
    }

    function stringifyValue(value) {
        if (value === null || value === undefined) return "—";
        if (typeof value === "boolean") return value ? "Sí" : "No";
        if (Array.isArray(value)) {
            return value.length > 0 ? value.join(", ") : "—";
        }
        return String(value);
    }
});