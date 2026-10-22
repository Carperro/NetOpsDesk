"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const compareBtn = document.getElementById("compare-btn");
    const clearBtn = document.getElementById("clear-btn");
    const configA = document.getElementById("config-a");
    const configB = document.getElementById("config-b");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const diffOutput = document.getElementById("diff-output");

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

    clearBtn.addEventListener("click", () => {
        configA.value = "";
        configB.value = "";
        errorArea.hidden = true;
        resultContainer.hidden = true;
    });

    compareBtn.addEventListener("click", async () => {
        errorArea.hidden = true;
        resultContainer.hidden = true;
        diffOutput.innerHTML = '';

        const originalText = compareBtn.textContent;
        compareBtn.textContent = "Comparando...";
        compareBtn.disabled = true;

        const payload = {
            config_a: configA.value,
            config_b: configB.value
        };

        try {
            const res = await fetch("/api/v1/tools/config-comparator/compare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            renderDiff(data);
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            compareBtn.disabled = false;
            compareBtn.textContent = originalText;
        }
    });

    function renderDiff(data) {
        if (!data.has_changes) {
            const p = document.createElement("p");
            p.textContent = "No hay diferencias. Ambas configuraciones son idénticas.";
            p.style.color = "var(--text-muted)";
            p.style.textAlign = "center";
            p.style.padding = "2rem";
            diffOutput.appendChild(p);
            resultContainer.hidden = false;
            return;
        }

        data.diff_lines.forEach(line => {
            const lineDiv = document.createElement("div");
            lineDiv.className = "diff-line";
            
            // Asignar clases según el tipo de línea
            if (line.startsWith("+")) {
                lineDiv.classList.add("diff-add");
            } else if (line.startsWith("-")) {
                lineDiv.classList.add("diff-del");
            } else if (line.startsWith("@@")) {
                lineDiv.classList.add("diff-header");
            } else {
                lineDiv.classList.add("diff-context");
            }

            // Usamos textContent para prevenir XSS
            lineDiv.textContent = line;
            diffOutput.appendChild(lineDiv);
        });

        resultContainer.hidden = false;
    }
});