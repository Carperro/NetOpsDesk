"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("traceroute-form");
    if (!form) return;

    const hostInput = document.getElementById("host-input");
    const hopsInput = document.getElementById("hops-input");
    const executeBtn = document.getElementById("execute-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const tbody = document.getElementById("hops-tbody");

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
        await submitTraceroute();
    });

    async function submitTraceroute() {
        clearOutputs();
        
        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Trazando ruta...";
        form.setAttribute("aria-busy", "true");
        executeBtn.disabled = true;

        const payload = {
            host: hostInput.value.trim(),
            max_hops: parseInt(hopsInput.value, 10)
        };

        try {
            const response = await fetch("/api/v1/tools/traceroute/execute", {
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
        tbody.innerHTML = '';
    }

    function renderResult(data) {
        document.getElementById("result-host").textContent = data.host;
        document.getElementById("result-resolved-ip").textContent = data.resolved_ip || "—";

        if (!data.hops || data.hops.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color: var(--text-muted);">No se pudieron trazar saltos hacia este destino.</td></tr>';
            resultContainer.hidden = false;
            return;
        }
        
        data.hops.forEach(hop => {
            const tr = document.createElement("tr");
            
            // Salto
            const tdHop = document.createElement("td");
            tdHop.textContent = hop.hop_number;
            // Si es el último salto (el destino), lo resaltamos
            if (hop.ip === data.resolved_ip) {
                tdHop.style.fontWeight = "bold";
                tdHop.style.color = "var(--primary)";
            }
            
            // IP
            const tdIp = document.createElement("td");
            tdIp.textContent = hop.ip || "*"; // Asterisco si es timeout
            
            // Tiempos
            const tdTimes = document.createElement("td");
            if (hop.times_ms.length > 0) {
                // Unimos los tiempos con " / " (ej. "12 / 14 / 15")
                tdTimes.textContent = hop.times_ms.join(" / ");
            } else {
                tdTimes.textContent = "*";
            }

            tr.appendChild(tdHop);
            tr.appendChild(tdIp);
            tr.appendChild(tdTimes);
            tbody.appendChild(tr);
        });

        resultContainer.hidden = false;
    }
});