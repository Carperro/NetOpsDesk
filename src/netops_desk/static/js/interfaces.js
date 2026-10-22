"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const executeBtn = document.getElementById("execute-btn");
    if (!executeBtn) return;

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

    executeBtn.addEventListener("click", async () => {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultContainer.hidden = true;
        resultContainer.innerHTML = '';

        const originalText = executeBtn.textContent;
        executeBtn.textContent = "Escaneando...";
        executeBtn.disabled = true;

        try {
            const response = await fetch("/api/v1/tools/interfaces/execute", { method: "GET" }).catch(() => null);

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
        if (!data.interfaces || data.interfaces.length === 0) {
            resultContainer.innerHTML = '<p class="text-muted">No se encontraron interfaces.</p>';
            resultContainer.hidden = false;
            return;
        }

        data.interfaces.forEach(iface => {
            const card = document.createElement("div");
            card.className = "interface-card";

            const isUpClass = iface.is_up ? "status-up" : "status-down";
            const stateText = iface.is_up ? "Activo" : "Desconectado";

            // Construimos el DOM de forma segura
            const header = document.createElement("div");
            header.className = "iface-header";
            
            const title = document.createElement("h3");
            title.textContent = iface.name;
            
            const badge = document.createElement("span");
            badge.className = `badge ${isUpClass}`;
            badge.textContent = stateText;

            header.appendChild(title);
            header.appendChild(badge);

            const list = document.createElement("ul");
            list.className = "iface-details";

            const details = [
                { label: "MAC", value: iface.mac_address || "N/A" },
                { label: "IPv4", value: iface.ipv4 || "N/A" },
                { label: "Máscara", value: iface.netmask || "N/A" },
                { label: "Gateway", value: iface.gateway || "N/A" },
                { label: "DNS", value: iface.dns_servers && iface.dns_servers.length ? iface.dns_servers.join(", ") : "N/A" },
                { label: "Velocidad", value: iface.speed_mbps > 0 ? `${iface.speed_mbps} Mbps` : "N/A" }
            ];

            details.forEach(d => {
                const li = document.createElement("li");
                const spanLabel = document.createElement("span");
                spanLabel.className = "iface-label";
                spanLabel.textContent = d.label;
                const spanValue = document.createElement("span");
                spanValue.className = "iface-value";
                spanValue.textContent = d.value;
                
                li.appendChild(spanLabel);
                li.appendChild(spanValue);
                list.appendChild(li);
            });

            card.appendChild(header);
            card.appendChild(list);
            resultContainer.appendChild(card);
        });

        resultContainer.hidden = false;
    }
});