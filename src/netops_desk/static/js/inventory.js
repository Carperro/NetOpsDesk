"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("device-form");
    if (!form) return;

    const tbody = document.getElementById("devices-tbody");
    const errorArea = document.getElementById("error-container");
    const saveBtn = document.getElementById("save-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    
    // Campos
    const idInput = document.getElementById("device-id");
    const nameInput = document.getElementById("name-input");
    const ipInput = document.getElementById("ip-input");
    const typeInput = document.getElementById("type-input");
    const locInput = document.getElementById("location-input");
    const notesInput = document.getElementById("notes-input");

    const API_URL = "/api/v1/tools/inventory/devices";

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

    async function loadDevices() {
        tbody.innerHTML = '';
        try {
            const res = await fetch(API_URL);
            if (!res.ok) throw new Error();
            const devices = await res.json();
            renderTable(devices);
        } catch {
            showAlert(errorArea, 'Error al cargar los dispositivos.', 'error', 'Error de red');
        }
    }

    function renderTable(devices) {
        if (devices.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.textContent = "No hay dispositivos registrados.";
            td.style.textAlign = "center";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        devices.forEach(d => {
            const tr = document.createElement("tr");
            
            const fields = [d.ip_address, d.name, d.device_type || "-", d.location || "-"];
            fields.forEach(text => {
                const td = document.createElement("td");
                td.textContent = text;
                tr.appendChild(td);
            });

            // Botones de acción
            const tdActions = document.createElement("td");
            tdActions.className = "actions-cell";
            
            const editBtn = document.createElement("button");
            editBtn.className = "btn-icon edit";
            editBtn.textContent = "✏️";
            editBtn.title = "Editar";
            editBtn.onclick = () => startEdit(d);

            const delBtn = document.createElement("button");
            delBtn.className = "btn-icon delete";
            delBtn.textContent = "🗑️";
            delBtn.title = "Eliminar";
            delBtn.setAttribute("aria-label", `Eliminar dispositivo ${d.name}`);
            delBtn.onclick = () => deleteDevice(d.id, delBtn);

            tdActions.appendChild(editBtn);
            tdActions.appendChild(delBtn);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });
    }

    function startEdit(device) {
        idInput.value = device.id;
        nameInput.value = device.name;
        ipInput.value = device.ip_address;
        typeInput.value = device.device_type || "";
        locInput.value = device.location || "";
        notesInput.value = device.notes || "";
        
        saveBtn.textContent = "Guardar Cambios";
        cancelBtn.hidden = false;
        nameInput.focus();
    }

    function resetForm() {
        form.reset();
        idInput.value = "";
        saveBtn.textContent = "Agregar Dispositivo";
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
            name: nameInput.value.trim(),
            ip_address: ipInput.value.trim(),
            device_type: typeInput.value.trim(),
            location: locInput.value.trim(),
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
            loadDevices();
        } catch {
            showAlert(errorArea, 'Error de conexión.', 'error', 'Red');
        } finally {
            saveBtn.disabled = false;
            if (saveBtn.textContent === "Guardando...") saveBtn.textContent = idleLabel;
            saveBtn.removeAttribute("aria-busy");
        }
    });

    async function deleteDevice(id, button) {
        if (!confirm("¿Estás seguro de eliminar este dispositivo?")) return;
        
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        try {
            const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
            if (res.ok) loadDevices();
        } catch {
            showAlert(errorArea, 'Error al eliminar.', 'error', 'Red');
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    }

    // Carga inicial
    loadDevices();
});
