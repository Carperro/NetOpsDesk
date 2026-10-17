(function () {
  'use strict';

  const THEME_STORAGE_KEY = 'netops-desk-theme';
  const API_ENDPOINT = '/api/v1/tools/ipv4/calculate';
  const unavailableText = 'No disponible para este prefijo y modo';

  const themeToggle = document.getElementById('theme-toggle');
  const themeLabel = themeToggle?.querySelector('.theme-toggle__label');
  const operationInputs = Array.from(document.querySelectorAll('input[name="operation"]'));
  const operationPanels = Array.from(document.querySelectorAll('.operation-panel'));

  let requestVersion = 0;
  let activeRequest = null;

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (_) {
      // La preferencia no debe impedir el cambio durante la sesión.
    }
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    const actionLabel = isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
    document.documentElement.setAttribute('data-theme', theme);
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isDark));
      themeToggle.setAttribute('aria-label', actionLabel);
    }
    if (themeLabel) themeLabel.textContent = actionLabel;
  }

  function initTheme() {
    const stored = getStoredTheme();
    applyTheme(stored === 'dark' || stored === 'light' ? stored : 'dark');
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    setStoredTheme(next);
  }

  if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
  initTheme();

  const errorMessages = {
    method_not_allowed: 'El método de solicitud no está permitido.',
    unsupported_media_type: 'El tipo de contenido no es compatible.',
    invalid_json: 'El cuerpo de la solicitud no es JSON válido.',
    invalid_body: 'El cuerpo de la solicitud debe ser un objeto JSON.',
    unknown_field: 'La solicitud contiene campos no reconocidos.',
    incompatible_inputs: 'Combiná los campos de una sola operación.',
    missing_field: 'Falta un campo obligatorio.',
    invalid_type: 'El tipo de dato de uno de los campos no es válido.',
    invalid_value: 'Uno de los valores ingresados no es válido.',
    non_contiguous_netmask: 'La máscara de subred debe ser contigua.',
    insufficient_capacity: 'La cantidad de hosts supera la capacidad IPv4 admitida.',
    internal_error: 'Ocurrió un error interno. Intentá de nuevo más tarde.'
  };

  const forms = [
    {
      operation: 'direct-cidr',
      formId: 'form-direct-cidr',
      resultId: 'result-direct-cidr',
      warningId: 'warnings-direct-cidr',
      errorId: 'error-direct-cidr',
      buildPayload: (formData) => ({
        cidr: formData.get('cidr').trim(),
        mode: formData.get('mode')
      })
    },
    {
      operation: 'direct-address',
      formId: 'form-direct-address',
      resultId: 'result-direct-address',
      warningId: 'warnings-direct-address',
      errorId: 'error-direct-address',
      buildPayload: (formData) => ({
        address: formData.get('address').trim(),
        netmask: formData.get('netmask').trim(),
        mode: formData.get('mode')
      })
    },
    {
      operation: 'inverse',
      formId: 'form-inverse',
      resultId: 'result-inverse',
      warningId: 'warnings-inverse',
      errorId: 'error-inverse',
      buildPayload: (formData) => {
        const rawValue = formData.get('required_hosts').trim();
        if (!/^\d+$/.test(rawValue)) {
          throw new Error('Ingresá una cantidad entera de hosts, sin decimales ni notación científica.');
        }
        const value = Number(rawValue);
        if (!Number.isSafeInteger(value) || value < 1) {
          throw new Error('La cantidad de hosts debe ser un entero seguro mayor o igual que 1.');
        }
        return {
          required_hosts: value,
          mode: formData.get('mode')
        };
      }
    }
  ];

  function getElement(id) {
    return document.getElementById(id);
  }

  function clearOutputs(config) {
    const result = getElement(config.resultId);
    const warnings = getElement(config.warningId);
    const error = getElement(config.errorId);
    if (result) result.replaceChildren();
    if (warnings) warnings.replaceChildren();
    if (error) error.textContent = '';
    const form = getElement(config.formId);
    const status = form?.querySelector('.operation-status');
    if (status) status.textContent = '';
  }

  function clearAllOutputs() {
    forms.forEach(clearOutputs);
  }

  function setError(config, message) {
    const error = getElement(config.errorId);
    if (error) error.textContent = message;
  }

  function setBusy(config, busy) {
    const form = getElement(config.formId);
    if (!form) return;
    form.setAttribute('aria-busy', String(busy));
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.operation-status');
    if (button) {
      if (!button.dataset.idleLabel) button.dataset.idleLabel = button.textContent;
      button.disabled = busy;
      button.textContent = busy ? 'Calculando…' : button.dataset.idleLabel;
    }
    if (status && busy) {
      status.textContent = 'Calculando…';
    } else if (status && status.textContent === 'Calculando…') {
      status.textContent = '';
    }
  }

  function cancelActiveRequest() {
    requestVersion += 1;
    if (activeRequest) {
      activeRequest.controller.abort();
      setBusy(activeRequest.config, false);
      activeRequest = null;
    }
  }

  function makeElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function displayValue(value) {
    if (value === null || value === undefined) return unavailableText;
    if (typeof value === 'string' || typeof value === 'number') return String(value);
    return 'Respuesta no disponible';
  }

  function appendResultField(list, label, value, featured) {
    const item = makeElement('div', featured ? 'result-item result-item--featured' : 'result-item');
    item.append(makeElement('dt', 'result-item__label', label));
    item.append(makeElement('dd', 'result-item__value', displayValue(value)));
    list.append(item);
  }

  function appendBinaryDetails(result, binary) {
    const details = makeElement('details', 'binary-details');
    details.append(makeElement('summary', '', 'Ver representación binaria'));
    const list = makeElement('dl', 'result-grid result-grid--binary');
    const fields = [
      ['network', 'Red'],
      ['broadcast', 'Broadcast'],
      ['netmask', 'Máscara'],
      ['wildcard', 'Wildcard'],
      ['first_usable', 'Primera utilizable'],
      ['last_usable', 'Última utilizable']
    ];
    fields.forEach(([key, label]) => appendResultField(list, label, binary?.[key], false));
    details.append(list);
    result.append(details);
  }

  function renderResult(config, data) {
    const result = getElement(config.resultId);
    if (!result) return;

    const list = makeElement('dl', 'result-grid');
    const isInverse = config.operation === 'inverse';
    if (isInverse) {
      appendResultField(list, 'Hosts requeridos', data.required_hosts, false);
      appendResultField(list, 'Modo solicitado', data.mode_requested, false);
      appendResultField(list, 'Modo aplicado', data.mode_applied, false);
      appendResultField(list, 'Prefijo', data.prefix === null || data.prefix === undefined ? data.prefix : `/${data.prefix}`, true);
      appendResultField(list, 'Direcciones totales', data.total_addresses, false);
      appendResultField(list, 'Direcciones utilizables', data.usable_addresses, true);
    } else {
      appendResultField(list, 'Red', data.network, true);
      appendResultField(list, 'Broadcast', data.broadcast, true);
      appendResultField(list, 'Máscara', data.netmask, true);
      appendResultField(list, 'Wildcard', data.wildcard, false);
      appendResultField(list, 'Primera utilizable', data.first_usable, false);
      appendResultField(list, 'Última utilizable', data.last_usable, false);
      appendResultField(list, 'Direcciones totales', data.total_addresses, true);
      appendResultField(list, 'Direcciones utilizables', data.usable_addresses, true);
    }
    result.replaceChildren(list);
    if (!isInverse) appendBinaryDetails(result, data.binary);
  }

  function renderWarnings(config, warnings) {
    const list = getElement(config.warningId);
    if (!list || !Array.isArray(warnings)) return;
    const items = warnings.map((warning) => {
      const item = makeElement('li', 'warning-item');
      const code = warning && typeof warning.code === 'string' ? warning.code : 'warning';
      const message = warning && typeof warning.message === 'string'
        ? warning.message
        : 'La API devolvió una advertencia sin detalle.';
      item.append(makeElement('strong', 'warning-item__code', code));
      item.append(makeElement('p', 'warning-item__message', message));
      return item;
    });
    list.replaceChildren(...items);
  }

  function formatApiError(data) {
    const code = typeof data?.error === 'string' ? data.error : 'unknown_error';
    const detail = typeof data?.detail === 'string' ? data.detail.trim() : '';
    if (!Object.prototype.hasOwnProperty.call(errorMessages, code)) {
      return detail
        ? `La solicitud no pudo completarse (${code}). ${detail}`
        : `La solicitud no pudo completarse. Código: ${code}.`;
    }
    const friendly = errorMessages[code];
    return detail && detail !== friendly ? `${friendly} ${detail}` : friendly;
  }

  function selectOperation(operation) {
    cancelActiveRequest();
    clearAllOutputs();
    operationPanels.forEach((panel) => {
      panel.hidden = panel.id !== `panel-${operation}`;
    });
  }

  operationInputs.forEach((input) => {
    input.addEventListener('change', () => {
      if (input.checked) selectOperation(input.value);
    });
  });

  async function handleSubmit(config, event) {
    event.preventDefault();
    cancelActiveRequest();
    clearOutputs(config);

    const form = event.currentTarget;
    const formData = new FormData(form);
    let payload;
    try {
      payload = config.buildPayload(formData);
    } catch (error) {
      setError(config, error instanceof Error ? error.message : 'Revisá los datos ingresados.');
      return;
    }

    const controller = new AbortController();
    const version = requestVersion;
    activeRequest = { controller, config, version };
    setBusy(config, true);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json'
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      let data;
      try {
        data = await response.json();
      } catch (_) {
        if (version === requestVersion) {
          setError(config, 'La respuesta del servidor no contiene JSON válido. Podés reintentar.');
        }
        return;
      }

      if (version !== requestVersion) return;
      if (!data || typeof data !== 'object' || Array.isArray(data)) {
        setError(config, 'La respuesta del servidor tiene un formato inesperado. Podés reintentar.');
        return;
      }
      if (!response.ok) {
        setError(config, formatApiError(data));
        return;
      }

      renderResult(config, data);
      renderWarnings(config, data.warnings);
      const status = form.querySelector('.operation-status');
      if (status) status.textContent = 'Cálculo completado.';
    } catch (error) {
      if (version !== requestVersion || error?.name === 'AbortError') return;
      setError(config, 'No se pudo conectar con el servidor. Verificá la conexión e intentá de nuevo.');
    } finally {
      if (version === requestVersion) {
        setBusy(config, false);
        activeRequest = null;
      }
    }
  }

  forms.forEach((config) => {
    const form = getElement(config.formId);
    if (form) form.addEventListener('submit', (event) => handleSubmit(config, event));
  });

  const initialOperation = operationInputs.find((input) => input.checked)?.value || 'direct-cidr';
  operationPanels.forEach((panel) => {
    panel.hidden = panel.id !== `panel-${initialOperation}`;
  });
})();
