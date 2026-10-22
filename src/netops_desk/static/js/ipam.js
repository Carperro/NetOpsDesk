"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("ipam-form");
    if (!form) return;

    const tbody = document.getElementById("ips-tbody");
    const errorArea = document.getElementById("error-container");
    const saveBtn = document.getElementById("save-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    
    const idInput = document.getElementById("record-id");
    const ipInput = document.getElementById("ip-input");
    const statusInput = document.getElementById("status-input");
    const assignedInput = document.getElementById("assigned-input");
    const notesInput = document.getElementById("notes-input");

    const API_URL = "/api/v1/tools/ipam/addresses";

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

    async function loadIps() {
        tbody.innerHTML = '';
        try {
            const res = await fetch(API_URL);
            if (!res.ok) throw new Error();
            const ips = await res.json();
            renderTable(ips);
        } catch {
            showAlert(errorArea, 'Error al cargar las direcciones.', 'error', 'Error de red');
        }
    }

    function renderTable(ips) {
        if (ips.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.textContent = "No hay direcciones registradas.";
            td.style.textAlign = "center";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        ips.forEach(ip => {
            const tr = document.createElement("tr");
            
            const tdIp = document.createElement("td");
            tdIp.textContent = ip.ip_address;
            tdIp.style.fontWeight = "bold";
            
            const tdStatus = document.createElement("td");
            const badge = document.createElement("span");
            badge.className = `badge-status badge-${ip.status}`;
            badge.textContent = ip.status.toUpperCase();
            tdStatus.appendChild(badge);
            
            const tdAssigned = document.createElement("td");
            tdAssigned.textContent = ip.assigned_to || "-";
            
            const tdNotes = document.createElement("td");
            tdNotes.textContent = ip.notes || "-";

            const tdActions = document.createElement("td");
            tdActions.className = "actions-cell";
            
            const editBtn = document.createElement("button");
            editBtn.className = "btn-icon edit";
            editBtn.textContent = "✏️";
            editBtn.title = "Editar";
            editBtn.onclick = () => startEdit(ip);

            const delBtn = document.createElement("button");
            delBtn.className = "btn-icon delete";
            delBtn.textContent = "🗑️";
            delBtn.title = "Eliminar";
            delBtn.setAttribute("aria-label", `Eliminar asignación de ${ip.ip_address}`);
            delBtn.onclick = () => deleteRecord(ip.id, delBtn);

            tdActions.appendChild(editBtn);
            tdActions.appendChild(delBtn);

            tr.appendChild(tdIp);
            tr.appendChild(tdStatus);
            tr.appendChild(tdAssigned);
            tr.appendChild(tdNotes);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });
    }

    function startEdit(ip) {
        idInput.value = ip.id;
        ipInput.value = ip.ip_address;
        statusInput.value = ip.status;
        assignedInput.value = ip.assigned_to || "";
        notesInput.value = ip.notes || "";
        
        saveBtn.textContent = "Guardar Cambios";
        cancelBtn.hidden = false;
        ipInput.focus();
    }

    function resetForm() {
        form.reset();
        idInput.value = "";
        saveBtn.textContent = "Registrar IP";
        cancelBtn.hidden = true;
        errorArea.hidden = true;
    }

    cancelBtn.addEventListener("click", resetForm);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorArea.hidden = true;
        const idleLabel = saveBtn.textContent;
        saveBtn.disabled = true;
        saveBtn.textContent = "Guardando...";
        saveBtn.setAttribute("aria-busy", "true");

        const payload = {
            ip_address: ipInput.value.trim(),
            status: statusInput.value,
            assigned_to: assignedInput.value.trim(),
            notes: notesInput.value.trim()
        };

        const isEdit = idInput.value !== "";
        const url = isEdit ? `${API_URL}/${idInput.value}` : API_URL;
        const method = isEdit ? "PUT" : "POST";

        try {
            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json().catch(() => null);

            if (!res.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(res, data), 'error', NetOpsApiErrors.title(res));
                return;
            }

            resetForm();
            loadIps();
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            saveBtn.disabled = false;
            if (saveBtn.textContent === "Guardando...") saveBtn.textContent = idleLabel;
            saveBtn.removeAttribute("aria-busy");
        }
    });

    async function deleteRecord(id, button) {
        if (!confirm("¿Estás seguro de eliminar esta dirección IP?")) return;
        
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        try {
            const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
            if (res.ok) loadIps();
        } catch {
            showAlert(errorArea, 'Error al eliminar.', 'error', 'Red');
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    }

    // Carga inicial
    loadIps();
});
