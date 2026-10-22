"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("report-form");
    if (!form) return;

    const findingsContainer = document.getElementById("findings-container");
    const addFindingBtn = document.getElementById("add-finding-btn");
    const generateBtn = document.getElementById("generate-btn");
    const copyBtn = document.getElementById("copy-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const markdownOutput = document.getElementById("markdown-output");

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

    function addFindingRow() {
        const row = document.createElement("div");
        row.className = "finding-row";

        const stepInput = document.createElement("input");
        stepInput.type = "text";
        stepInput.className = "form-input finding-step";
        stepInput.placeholder = "Paso (ej. Ping al Gateway)";
        
        const resultInput = document.createElement("input");
        resultInput.type = "text";
        resultInput.className = "form-input finding-result";
        resultInput.placeholder = "Resultado (ej. Exitoso)";

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "btn-icon delete";
        deleteBtn.textContent = "🗑️";
        deleteBtn.onclick = () => row.remove();

        row.appendChild(stepInput);
        row.appendChild(resultInput);
        row.appendChild(deleteBtn);
        findingsContainer.appendChild(row);
    }

    addFindingRow();
    addFindingBtn.addEventListener("click", addFindingRow);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorArea.hidden = true;
        resultContainer.hidden = true;

        const findings = [];
        const rows = findingsContainer.querySelectorAll(".finding-row");
        
        rows.forEach(row => {
            const step = row.querySelector(".finding-step").value.trim();
            const result = row.querySelector(".finding-result").value.trim();
            if (step || result) {
                findings.push({ step, result });
            }
        });

        const payload = {
            title: document.getElementById("title-input").value.trim(),
            author: document.getElementById("author-input").value.trim() || null,
            conclusion: document.getElementById("conclusion-input").value.trim() || null,
            findings: findings
        };

        const originalText = generateBtn.textContent;
        generateBtn.textContent = "Generando...";
        generateBtn.disabled = true;

        try {
            const res = await fetch("/api/v1/tools/report-generator/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                // Si NetOpsApiErrors falla, mostramos el JSON crudo para debug
                let errorMsg = "Error desconocido";
                let errorTitle = "Error";
                
                if (typeof NetOpsApiErrors !== "undefined") {
                    errorMsg = NetOpsApiErrors.message(res, data);
                    errorTitle = NetOpsApiErrors.title(res);
                } else if (data && data.detail) {
                    errorMsg = data.detail;
                }
                
                showAlert(errorArea, errorMsg, 'error', errorTitle);
                return;
            }

            markdownOutput.value = data.report_markdown;
            resultContainer.hidden = false;
        } catch (error) {
            // ESTO ES CLAVE PARA DEBUGGEAR
            console.error("Error capturado en el frontend:", error);
            showAlert(errorArea, 'Error de conexión o error interno de JS (Revisar F12).', 'error', 'Red');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = originalText;
        }
    });

    copyBtn.addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(markdownOutput.value);
            const original = copyBtn.textContent;
            copyBtn.textContent = "¡Copiado!";
            setTimeout(() => copyBtn.textContent = original, 2000);
        } catch {
            showAlert(errorArea, 'No se pudo copiar al portapapeles.', 'error');
        }
    });
});