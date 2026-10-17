document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('vlsm-form');
    const container = document.getElementById('requirements-container');
    const addBtn = document.getElementById('add-req-btn');
    const resultsContainer = document.getElementById('vlsm-results');
    const errorArea = document.getElementById('error-area');

    // 1. Función para agregar una nueva fila
    function addRequirementRow(name = '', hosts = '') {
        const row = document.createElement('div');
        row.className = 'requirement-row';
        row.innerHTML = `
            <input type="text" class="req-name" placeholder="Ej: Ventas" value="${name}" required>
            <input type="number" class="req-hosts" placeholder="Ej: 100" min="1" value="${hosts}" required>
            <button type="button" class="remove-req-btn" title="Eliminar">✕</button>
        `;
        
        // Agregar evento al botón de eliminar de esta fila
        row.querySelector('.remove-req-btn').addEventListener('click', () => {
            if (container.children.length > 1) {
                row.remove();
            } else {
                // Si es la última fila, solo limpiamos los inputs
                row.querySelector('.req-name').value = '';
                row.querySelector('.req-hosts').value = '';
            }
        });

        container.appendChild(row);
    }

    // 2. Evento para el botón de agregar
    addBtn.addEventListener('click', () => addRequirementRow());

    // 3. Evento de envío del formulario
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorArea.innerHTML = '';
        resultsContainer.hidden = true;

        const cidr = document.getElementById('network-cidr').value.trim();
        const rows = container.querySelectorAll('.requirement-row');
        
        const requirements = [];
        let hasError = false;

        rows.forEach(row => {
            const name = row.querySelector('.req-name').value.trim();
            const hosts = parseInt(row.querySelector('.req-hosts').value);

            if (!name || isNaN(hosts) || hosts < 1) {
                hasError = true;
            } else {
                requirements.push({ name, hosts });
            }
        });

        if (!cidr.includes('/')) {
            return showAlert(errorArea, "Falta el prefijo de red. Ej: 192.168.1.0/24", 'error', 'FORMATO INVÁLIDO');
        }
        if (hasError || requirements.length === 0) {
            return showAlert(errorArea, "Todos los departamentos deben tener un nombre y una cantidad de hosts válida.", 'error', 'DATOS INCOMPLETOS');
        }

        // Estado de carga
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Calculando...';

        try {
            const response = await fetch('/api/v1/tools/vlsm/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ network_cidr: cidr, requirements: requirements })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error al calcular VLSM.');
            }

            renderResults(data);
        } catch (error) {
            showAlert(errorArea, error.message, 'error', 'ERROR DE RED');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // 4. Renderizar resultados
    function renderResults(data) {
        const tbody = document.getElementById('vlsm-tbody');
        const remainingBox = document.getElementById('remaining-info');
        
        tbody.innerHTML = '';

        data.allocated.forEach(subnet => {
            const tr = document.createElement('tr');
            const cells = [
                subnet.name,
                `${subnet.network}/${subnet.prefix}`,
                subnet.netmask,
                `${subnet.first_host} - ${subnet.last_host}`,
                subnet.hosts_needed
            ];

            cells.forEach(text => {
                const td = document.createElement('td');
                td.textContent = text;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        // Mostrar espacio sobrante
        if (data.remaining && data.remaining.length > 0) {
            const rem = data.remaining[0];
            remainingBox.innerHTML = `
                <div class="alert alert--warning">
                    <div class="alert__header">Espacio Libre Sobrante</div>
                    <div class="alert__message">
                        Rango libre: <strong>${rem.network} - ${rem.broadcast}</strong> (${rem.total_ips} IPs disponibles)
                    </div>
                </div>
            `;
            remainingBox.hidden = false;
        } else {
            remainingBox.hidden = true;
        }

        resultsContainer.hidden = false;
    }

    // Utilidad de alertas (reutilizamos el mismo diseño)
    function showAlert(container, message, type = 'error', code = '') {
        if (!container) return;
        container.innerHTML = ''; 
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${type}`;
        alertDiv.innerHTML = `
            <div class="alert__header">${code || 'Error'}</div>
            <div class="alert__message">${message}</div>
        `;
        container.appendChild(alertDiv);
    }
});