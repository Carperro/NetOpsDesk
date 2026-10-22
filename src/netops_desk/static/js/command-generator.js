"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("command-form");
    if (!form) return;

    const typeSelect = document.getElementById("command-type");
    const targetInput = document.getElementById("target-input");
    const targetHelp = document.getElementById("target-help");
    const optionsContainer = document.getElementById("options-container");
    const generateBtn = document.getElementById("generate-btn");
    const errorArea = document.getElementById("error-container");
    const resultContainer = document.getElementById("result-container");
    const adminWarning = document.getElementById("admin-warning");

    // Catálogo local para la UI
    const UI_OPTIONS = {
        "ping": [{ val: "-t", label: "Continuo (-t)" }, { val: "-a", label: "Resolver IPs (-a)" }],
        "tracert": [{ val: "-d", label: "Sin resolver DNS (-d)" }],
        "nslookup": [],
        "ipconfig": [{ val: "/all", label: "Todo (/all)" }, { val: "/flushdns", label: "Limpiar caché DNS" }, { val: "/release", label: "Liberar IP" }, { val: "/renew", label: "Renovar IP" }],
        "netstat": [{ val: "-a", label: "Todas (-a)" }, { val: "-n", label: "Numérico (-n)" }, { val: "-b", label: "Ejecutables (-b)" }]
    };

    function updateUI() {
        const type = typeSelect.value;
        
        // Actualizar checkboxes
        optionsContainer.innerHTML = '';
        UI_OPTIONS[type].forEach(opt => {
            const label = document.createElement("label");
            label.className = "checkbox-label";
            
            const input = document.createElement("input");
            input.type = "checkbox";
            input.value = opt.val;
            input.className = "option-checkbox";
            
            label.appendChild(input);
            label.appendChild(document.createTextNode(" " + opt.label));
            optionsContainer.appendChild(label);
        });

        // Actualizar target
        if (type === "ipconfig" || type === "netstat") {
            targetInput.required = false;
            targetHelp.textContent = "Opcional para este comando.";
        } else {
            targetInput.required = true;
            targetHelp.textContent = "Requerido para este comando.";
        }
    }

    typeSelect.addEventListener("change", updateUI);
    updateUI(); // Carga inicial

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

        const options = Array.from(document.querySelectorAll(".option-checkbox:checked")).map(cb => cb.value);

        const payload = {
            command_type: typeSelect.value,
            target: targetInput.value.trim() || null,
            options: options
        };

        const originalText = generateBtn.textContent;
        generateBtn.textContent = "Generando...";
        generateBtn.disabled = true;

        try {
            const res = await fetch("/api/v1/tools/command-generator/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            document.getElementById("output-command").value = data.command;
            document.getElementById("output-explanation").textContent = data.explanation;
            adminWarning.hidden = !data.requires_admin;
            
            resultContainer.hidden = false;
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = originalText;
        }
    });

    document.getElementById("copy-btn").addEventListener("click", async () => {
        const text = document.getElementById("output-command").value;
        try {
            await navigator.clipboard.writeText(text);
            const btn = document.getElementById("copy-btn");
            const original = btn.textContent;
            btn.textContent = "¡Copiado!";
            setTimeout(() => btn.textContent = original, 2000);
        } catch {
            showAlert(errorArea, 'No se pudo copiar al portapapeles.', 'error');
        }
    });
});