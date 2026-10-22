"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("mtu-form");
    if (!form) return;

    const mtuInput = document.getElementById("mtu-input");
    const ipInput = document.getElementById("ip-input");
    const transportInput = document.getElementById("transport-input");
    const tunnelInput = document.getElementById("tunnel-input");
    const calculateBtn = document.getElementById("calculate-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const warningsList = document.getElementById("warnings-list");

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
        warningsList.innerHTML = '';
        warningsList.hidden = true;

        const originalText = calculateBtn.textContent;
        calculateBtn.textContent = "Calculando...";
        calculateBtn.disabled = true;

        const payload = {
            mtu: parseInt(mtuInput.value, 10),
            ip_version: ipInput.value,
            transport: transportInput.value,
            tunnel: tunnelInput.value
        };

        try {
            const res = await fetch("/api/v1/tools/mtu-calculator/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
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
            calculateBtn.disabled = false;
            calculateBtn.textContent = originalText;
        }
    });

    function renderResult(data) {
        document.getElementById("result-mss").textContent = data.mss;
        
        document.getElementById("math-mtu").textContent = data.mtu;
        document.getElementById("math-ip").textContent = data.ip_header_size;
        document.getElementById("math-transport").textContent = data.transport_header_size;
        document.getElementById("math-tunnel").textContent = data.tunnel_header_size;
        document.getElementById("math-result").textContent = data.mss;

                if (data.warnings && data.warnings.length > 0) {
            warningsList.hidden = false;
            
            // Mapeo para que se lea más amigable
            const warningTitles = {
                "packet_too_small": "PAQUETE MUY GRANDE",
                "mtu_below_minimum": "MTU MUY BAJO"
            };

            for (let i = 0; i < data.warnings.length; i += 2) {
                if (i + 1 < data.warnings.length) {
                    const code = data.warnings[i];
                    const message = data.warnings[i+1];
                    const friendlyTitle = warningTitles[code] || code.toUpperCase();
                    
                    const li = document.createElement("li");
                    
                    const strong = document.createElement("strong");
                    strong.textContent = friendlyTitle + ": ";
                    
                    const span = document.createElement("span");
                    span.textContent = message;
                    
                    li.appendChild(strong);
                    li.appendChild(span);
                    warningsList.appendChild(li);
                }
            }
        }

        resultContainer.hidden = false;
    }
});