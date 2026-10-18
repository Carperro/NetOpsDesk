/* Formatea errores HTTP para mostrarlos de manera coherente en la interfaz. */
(function () {
  'use strict';

  const messages = {
    bad_request: 'La solicitud no tiene un formato válido.',
    not_found: 'No se encontró el recurso solicitado.',
    method_not_allowed: 'La operación solicitada no está disponible.',
    unsupported_media_type: 'El formato enviado no es compatible. Enviá los datos como JSON.',
    invalid_json: 'El cuerpo de la solicitud no contiene JSON válido.',
    invalid_body: 'La solicitud debe contener un objeto JSON.',
    unknown_field: 'La solicitud contiene campos no reconocidos.',
    incompatible_inputs: 'Los datos ingresados corresponden a operaciones incompatibles.',
    missing_field: 'Falta completar uno o más campos obligatorios.',
    invalid_type: 'Uno de los datos tiene un tipo no válido.',
    invalid_value: 'Revisá los valores ingresados.',
    non_contiguous_netmask: 'La máscara de subred debe ser contigua.',
    insufficient_capacity: 'La red no tiene capacidad suficiente para ese cálculo.',
    validation_error: 'No se pudieron validar los datos enviados.',
    internal_error: 'Ocurrió un error interno. Intentá de nuevo más tarde.'
  };

  const detailCodes = new Set([
    'invalid_json', 'invalid_body', 'unknown_field', 'incompatible_inputs',
    'missing_field', 'invalid_type', 'invalid_value', 'non_contiguous_netmask',
    'insufficient_capacity', 'validation_error', 'unsupported_media_type'
  ]);

  function message(response, data) {
    const code = typeof data?.error === 'string' ? data.error : '';
    const detail = typeof data?.detail === 'string' ? data.detail.trim() : '';

    if (detail && detailCodes.has(code)) return detail;
    if (Object.prototype.hasOwnProperty.call(messages, code)) return messages[code];
    if (response?.status === 400) return 'No se pudo leer la solicitud. Revisá el formato JSON.';
    if (response?.status === 404) return 'No se encontró el recurso solicitado.';
    if (response?.status === 405) return 'La operación solicitada no está disponible.';
    if (response?.status === 415) return 'El formato enviado no es compatible. Enviá los datos como JSON.';
    if (response?.status === 422) return 'Revisá los datos ingresados e intentá de nuevo.';
    if (response?.status >= 500) return 'Ocurrió un error interno. Intentá de nuevo más tarde.';
    return 'No se pudo completar la solicitud. Revisá los datos e intentá de nuevo.';
  }

  function title(response) {
    if (response?.status === 415) return 'Formato no admitido';
    if (response?.status === 422) return 'Revisá los datos';
    if (response?.status >= 500) return 'Error del servidor';
    return 'No se pudo completar';
  }

  window.NetOpsApiErrors = { message, title };
})();
