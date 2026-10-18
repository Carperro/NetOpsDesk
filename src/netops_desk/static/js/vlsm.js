document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    const form = document.getElementById('vlsm-form');
    const container = document.getElementById('requirements-container');
    const addBtn = document.getElementById('add-req-btn');
    const resultsContainer = document.getElementById('vlsm-results');
    const errorArea = document.getElementById('error-area');

    // 1. Función para agregar una nueva fila
    function addRequirementRow(name = '', hosts = '') {
        const row = document.createElement('div');
        row.className = 'requirement-row';
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'req-name';
        nameInput.placeholder = 'Ej: Ventas';
        nameInput.value = name;
        nameInput.required = true;

        const hostsInput = document.createElement('input');
        hostsInput.type = 'number';
        hostsInput.className = 'req-hosts';
        hostsInput.placeholder = 'Ej: 100';
        hostsInput.min = '1';
        hostsInput.value = hosts;
        hostsInput.required = true;

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'remove-req-btn';
        removeButton.title = 'Eliminar';
        removeButton.textContent = '✕';

        row.append(nameInput, hostsInput, removeButton);
        
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
            }).catch(() => null);

            if (!response) {
                showAlert(errorArea, 'No se pudo conectar con el servidor. Verificá la conexión e intentá de nuevo.', 'error', 'Sin conexión');
                return;
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                showAlert(errorArea, NetOpsApiErrors.message(response, data), 'error', NetOpsApiErrors.title(response));
                return;
            }

            if (!data || typeof data !== 'object' || Array.isArray(data)) {
                showAlert(errorArea, 'El servidor devolvió una respuesta inválida. Intentá de nuevo.', 'error', 'Respuesta inválida');
                return;
            }

            renderResults(data);
        } catch {
            showAlert(errorArea, 'No se pudo procesar la respuesta. Revisá los datos e intentá de nuevo.', 'error', 'Error de cálculo');
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
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--warning';

            const header = document.createElement('div');
            header.className = 'alert__header';
            header.textContent = 'Espacio Libre Sobrante';

            const message = document.createElement('div');
            message.className = 'alert__message';
            const range = document.createElement('strong');
            range.textContent = `${rem.network} - ${rem.broadcast}`;
            message.append('Rango libre: ', range, ` (${rem.total_ips} IPs disponibles)`);

            alertDiv.append(header, message);
            remainingBox.replaceChildren(alertDiv);
            remainingBox.hidden = false;
        } else {
            remainingBox.hidden = true;
        }

        resultsContainer.hidden = false;
    }

    // Utilidad de alertas (reutilizamos el mismo diseño)
    function showAlert(container, message, type = 'error', code = '') {
        if (!container) return;
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${type}`;
        const header = document.createElement('div');
        header.className = 'alert__header';
        header.textContent = code || 'Error';

        const messageElement = document.createElement('div');
        messageElement.className = 'alert__message';
        messageElement.textContent = message;

        alertDiv.append(header, messageElement);
        container.replaceChildren(alertDiv);
    }
});
