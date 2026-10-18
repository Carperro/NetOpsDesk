document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    // --- 1. Variables de la UI ---
    const radios = document.querySelectorAll('input[name="operation"]');
    const panelCount = document.getElementById('panel-by-count');
    const panelHosts = document.getElementById('panel-by-hosts');
    const resultsContainer = document.getElementById('subnet-results');
    const errorArea = document.getElementById('error-area');
    const warningBanner = document.getElementById('normalization-warning');

    // --- 2. Función de Alertas Unificada ---
    function showAlert(container, message, type = 'error', code = '') {
        if (!container) return;
        container.innerHTML = ''; 
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${type}`;
        
        const header = document.createElement('div');
        header.className = 'alert__header';
        header.textContent = code || (type === 'error' ? 'Error' : 'Advertencia');
        
        const msg = document.createElement('div');
        msg.className = 'alert__message';
        msg.textContent = message;

        alertDiv.appendChild(header);
        alertDiv.appendChild(msg);
        container.appendChild(alertDiv);
    }

    // --- 3. Validación Estricta de CIDR ---
    function isValidCIDR(cidrString) {
        const parts = cidrString.split('/');
        if (parts.length !== 2) return false;

        const ip = parts[0];
        const prefix = parts[1];

        if (!/^\d+$/.test(prefix)) return false;
        const prefixNum = parseInt(prefix, 10);
        if (prefixNum < 0 || prefixNum > 32) return false;

        const octets = ip.split('.');
        if (octets.length !== 4) return false;

        for (let i = 0; i < octets.length; i++) {
            if (!/^\d+$/.test(octets[i])) return false;
            const num = parseInt(octets[i], 10);
            if (num < 0 || num > 255) return false;
        }
        return true;
    }

    // --- 4. Manejo de Pestañas ---
    radios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            panelCount.hidden = e.target.value !== 'by-count';
            panelHosts.hidden = e.target.value !== 'by-hosts';
            resultsContainer.hidden = true; 
            errorArea.innerHTML = ''; 
        });
    });

    // --- 5. Llamada a la API ---
    async function fetchSubnets(url, payload) {
        const submitBtn = document.querySelector(`#${payload.formId} button[type="submit"]`);
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Calculando...';
        resultsContainer.hidden = true;
        errorArea.replaceChildren();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload.data)
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
    }
    // --- 6. Listeners de Formularios ---
    document.getElementById('form-by-count').addEventListener('submit', (e) => {
        e.preventDefault();
        const cidr = document.getElementById('cidr-count').value.trim();
        const count = parseInt(document.getElementById('subnet-count').value);

        errorArea.innerHTML = '';
        resultsContainer.hidden = true;

        if (!isValidCIDR(cidr)) {
            showAlert(errorArea, "Usá el formato IPv4/CIDR, con octetos entre 0 y 255 y prefijo entre 0 y 32.", 'error', 'FORMATO INVÁLIDO');
            return;
        }
        if (isNaN(count) || count < 1) {
            showAlert(errorArea, "Ingresá una cantidad de subredes válida (número mayor a 0).", 'error', 'CANTIDAD INVÁLIDA');
            return;
        }

        fetchSubnets('/api/v1/tools/subnetting/by-count', {
            formId: 'form-by-count',
            data: { network_cidr: cidr, subnet_count: count }
        });
    });

    document.getElementById('form-by-hosts').addEventListener('submit', (e) => {
        e.preventDefault();
        const cidr = document.getElementById('cidr-hosts').value.trim();
        const hosts = parseInt(document.getElementById('required-hosts').value);

        errorArea.innerHTML = '';
        resultsContainer.hidden = true;

        if (!isValidCIDR(cidr)) {
            showAlert(errorArea, "Usá el formato IPv4/CIDR, con octetos entre 0 y 255 y prefijo entre 0 y 32.", 'error', 'FORMATO INVÁLIDO');
            return;
        }
        if (isNaN(hosts) || hosts < 1) {
            showAlert(errorArea, "Ingresá una cantidad de hosts válida (número mayor a 0).", 'error', 'CANTIDAD INVÁLIDA');
            return;
        }

        fetchSubnets('/api/v1/tools/subnetting/by-hosts', {
            formId: 'form-by-hosts',
            data: { network_cidr: cidr, required_hosts: hosts }
        });
    });

    // --- 7. Renderizado de la Tabla ---
    function renderResults(data) {
        const tbody = document.getElementById('subnet-tbody');
        tbody.innerHTML = ''; 

        if (data.was_normalized) {
            showAlert(warningBanner, `La IP ingresada fue ajustada a la red ${data.original_network}`, 'warning', 'IP NORMALIZADA');
            warningBanner.hidden = false;
        } else {
            warningBanner.hidden = true;
        }

        data.subnets.forEach((subnet, index) => {
            const tr = document.createElement('tr');
            
            let hostRange = 'N/A';
            if (subnet.first_host && subnet.last_host) {
                hostRange = `${subnet.first_host} - ${subnet.last_host}`;
            }

            const cells = [
                index + 1,
                subnet.network,
                `${subnet.netmask} (/${subnet.prefixlen})`,
                hostRange,
                subnet.broadcast
            ];

            cells.forEach(text => {
                const td = document.createElement('td');
                td.textContent = text;
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        resultsContainer.hidden = false;
    }
});