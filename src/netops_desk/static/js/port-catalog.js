"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const tbody = document.getElementById("ports-tbody");
    const errorArea = document.getElementById("error-container");

    const API_URL = "/api/v1/tools/port-catalog/search";
    let debounceTimer;

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

    async function fetchPorts(query) {
        tbody.innerHTML = '';
        errorArea.hidden = true;
        
        try {
            const res = await fetch(`${API_URL}?query=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error();
            const data = await res.json();
            renderTable(data.ports);
        } catch {
            showAlert(errorArea, 'Error al cargar el catálogo.', 'error', 'Red');
        }
    }

    function renderTable(ports) {
        if (ports.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 4;
            td.textContent = "No se encontraron puertos para esa búsqueda.";
            td.style.textAlign = "center";
            td.style.color = "var(--text-muted)";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        ports.forEach(p => {
            const tr = document.createElement("tr");
            
            const tdPort = document.createElement("td");
            tdPort.textContent = p.port;
            tdPort.style.fontWeight = "bold";
            tdPort.style.color = "var(--primary)";

            const tdProto = document.createElement("td");
            tdProto.textContent = p.protocol;
            
            const tdService = document.createElement("td");
            tdService.textContent = p.service;
            tdService.style.fontWeight = "600";

            const tdDesc = document.createElement("td");
            tdDesc.textContent = p.description;

            tr.appendChild(tdPort);
            tr.appendChild(tdProto);
            tr.appendChild(tdService);
            tr.appendChild(tdDesc);
            tbody.appendChild(tr);
        });
    }

    // Búsqueda en tiempo real (debounce de 300ms)
    searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchPorts(e.target.value);
        }, 300);
    });

    // Carga inicial
    fetchPorts("");
});