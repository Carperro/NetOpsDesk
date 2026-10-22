"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("history-form");
    if (!form) return;

    const tbody = document.getElementById("logs-tbody");
    const errorArea = document.getElementById("error-container");
    const clearAllBtn = document.getElementById("clear-all-btn");
    const submitBtn = form.querySelector('button[type="submit"]');

    const API_URL = "/api/v1/tools/history/logs";

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

    async function loadLogs() {
        tbody.innerHTML = '';
        try {
            const res = await fetch(API_URL);
            if (!res.ok) throw new Error();
            const logs = await res.json();
            renderTable(logs);
        } catch {
            showAlert(errorArea, 'Error al cargar el historial.', 'error', 'Red');
        }
    }

    function renderTable(logs) {
        if (logs.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 6;
            td.textContent = "No hay registros en el historial.";
            td.style.textAlign = "center";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement("tr");
            
            // Formatear fecha
            const dateObj = new Date(log.created_at);
            const dateStr = dateObj.toLocaleString("es-AR");

            const fields = [
                dateStr, 
                log.tool_name, 
                log.action, 
                log.result_status.toUpperCase(), 
                log.details || "-"
            ];
            
            fields.forEach((text, index) => {
                const td = document.createElement("td");
                td.textContent = text;
                
                if (index === 3) { // Estado
                    td.style.fontWeight = "bold";
                    if (text === "SUCCESS") td.style.color = "#10b981";
                    else if (text === "ERROR") td.style.color = "#ef4444";
                    else td.style.color = "#f59e0b";
                }
                tr.appendChild(td);
            });

            const tdActions = document.createElement("td");
            const delBtn = document.createElement("button");
            delBtn.className = "btn-icon delete";
            delBtn.textContent = "🗑️";
            delBtn.setAttribute("aria-label", `Eliminar registro de ${log.tool_name}`);
            delBtn.onclick = () => deleteLog(log.id, delBtn);
            tdActions.appendChild(delBtn);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorArea.hidden = true;
        const idleLabel = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Guardando...";
            submitBtn.setAttribute("aria-busy", "true");
        }

        const payload = {
            tool_name: document.getElementById("tool-input").value.trim(),
            action: document.getElementById("action-input").value.trim(),
            result_status: document.getElementById("status-input").value,
            details: document.getElementById("details-input").value.trim()
        };

        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            form.reset();
            loadLogs();
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = idleLabel;
                submitBtn.removeAttribute("aria-busy");
            }
        }
    });

    async function deleteLog(id, button) {
        if (!confirm("¿Eliminar este registro?")) return;
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        try {
            await fetch(`${API_URL}/${id}`, { method: "DELETE" });
            loadLogs();
        } catch {
            showAlert(errorArea, 'Error al eliminar.', 'error', 'Red');
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    }

    clearAllBtn.addEventListener("click", async () => {
        if (!confirm("¿Estás seguro de borrar TODO el historial? Esta acción no se puede deshacer.")) return;
        const idleLabel = clearAllBtn.textContent;
        clearAllBtn.disabled = true;
        clearAllBtn.textContent = "Borrando...";
        clearAllBtn.setAttribute("aria-busy", "true");
        try {
            await fetch(API_URL, { method: "DELETE" });
            loadLogs();
        } catch {
            showAlert(errorArea, 'Error al limpiar.', 'error', 'Red');
        } finally {
            clearAllBtn.disabled = false;
            clearAllBtn.textContent = idleLabel;
            clearAllBtn.removeAttribute("aria-busy");
        }
    });

    // Carga inicial
    loadLogs();
});
