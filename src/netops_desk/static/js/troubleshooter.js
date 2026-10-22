"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("trouble-form");
    if (!form) return;

    const select = document.getElementById("symptom-select");
    const diagnoseBtn = document.getElementById("diagnose-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const causesContainer = document.getElementById("causes-container");

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
        causesContainer.innerHTML = '';

        const originalText = diagnoseBtn.textContent;
        diagnoseBtn.textContent = "Analizando...";
        diagnoseBtn.disabled = true;

        const symptomId = select.value;

        try {
            const res = await fetch(`/api/v1/tools/troubleshooter/symptoms/${symptomId}`);
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            renderResult(data);
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            diagnoseBtn.disabled = false;
            diagnoseBtn.textContent = originalText;
        }
    });

    function renderResult(data) {
        document.getElementById("result-symptom-name").textContent = data.symptom_name;

        data.causes.forEach((cause, index) => {
            const card = document.createElement("div");
            card.className = "cause-card";

            // Header clickeable para el acordeón
            const header = document.createElement("button");
            header.type = "button";
            header.className = "cause-header";
            
            const title = document.createElement("span");
            title.className = "cause-title";
            title.textContent = `Causa ${index + 1}: ${cause.cause}`;
            
            const icon = document.createElement("span");
            icon.className = "cause-icon";
            icon.textContent = "▼"; // Flecha hacia abajo

            header.appendChild(title);
            header.appendChild(icon);

            // Contenedor de los pasos (oculto por defecto)
            const body = document.createElement("div");
            body.className = "cause-body";
            body.hidden = true;

            const list = document.createElement("ul");
            list.className = "steps-list";

            cause.steps.forEach(step => {
                const li = document.createElement("li");
                li.textContent = step;
                list.appendChild(li);
            });

            body.appendChild(list);

            // Lógica del acordeón
            header.addEventListener("click", () => {
                const isHidden = body.hidden;
                body.hidden = !isHidden;
                icon.textContent = isHidden ? "▲" : "▼";
                card.classList.toggle("active", isHidden);
            });

            card.appendChild(header);
            card.appendChild(body);
            causesContainer.appendChild(card);
        });

        resultContainer.hidden = false;
    }
});