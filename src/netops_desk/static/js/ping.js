"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("ping-form");
    if (!form) return;

    const hostInput = document.getElementById("host-input");
    const countInput = document.getElementById("count-input");
    const executeBtn = document.getElementById("execute-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const responsesSection = document.getElementById("responses-section");
    const tbody = document.getElementById("responses-tbody");

    const fields = {
        host: document.getElementById("result-host"),
        resolved_ip: document.getElementById("result-resolved-ip"),
        packets_sent: document.getElementById("result-sent"),
        packets_received: document.getElementById("result-received"),
        packet_loss_percent: document.getElementById("result-loss"),
    };

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
        await submitPing();
    });

    async function submitPing() {
        clearOutputs();
        form.setAttribute("aria-busy", "true");
        executeBtn.disabled = true;

        const payload = {
            host: hostInput.value.trim(),
            count: parseInt(countInput.value, 10)
        };

        try {
            const response = await fetch("/api/v1/tools/ping/execute", {
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
        }
    }

    function clearOutputs() {
        errorArea.innerHTML = '';
        errorArea.hidden = true;
        resultContainer.hidden = true;
        responsesSection.hidden = true;
        tbody.innerHTML = '';
        for (const el of Object.values(fields)) {
            if (el) el.textContent = "—";
        }
    }

    function renderResult(data) {
        fields.host.textContent = data.host;
        fields.resolved_ip.textContent = data.resolved_ip || "—";
        fields.packets_sent.textContent = data.packets_sent;
        fields.packets_received.textContent = data.packets_received;
        fields.packet_loss_percent.textContent = `${data.packet_loss_percent.toFixed(1)}%`;

        const timesEl = document.getElementById("result-times");
        if (data.min_ms !== null) {
            timesEl.textContent = `${data.min_ms} / ${data.max_ms} / ${data.avg_ms.toFixed(1)}`;
        } else {
            timesEl.textContent = "— / — / —";
        }

        // Renderizar tabla si hay respuestas
        if (data.responses && data.responses.length > 0) {
            responsesSection.hidden = false;
            data.responses.forEach(r => {
                const tr = document.createElement("tr");
                
                const tdSeq = document.createElement("td");
                tdSeq.textContent = r.seq;
                
                const tdTime = document.createElement("td");
                tdTime.textContent = r.time_ms;
                
                tr.appendChild(tdSeq);
                tr.appendChild(tdTime);
                tbody.appendChild(tr);
            });
        }

        // Alerta de pérdida (opcional, para que quede lindo visualmente)
        if (data.packet_loss_percent === 100) {
            showAlert(errorArea, "El host no respondió a ningún paquete. Puede estar apagado o bloqueando ICMP.", "warning", "100% de pérdida");
        } else if (data.packet_loss_percent > 0) {
            showAlert(errorArea, `Se perdió el ${data.packet_loss_percent}% de los paquetes.`, "warning", "Pérdida parcial");
        }

        resultContainer.hidden = false;
    }
});