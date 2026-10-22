/* Formatea errores HTTP para mostrarlos de manera coherente en la interfaz. */
(function () {
  'use strict';

  const messages = {
    // Módulo 1 (Redes básicas)
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
    internal_error: 'Ocurrió un error interno. Intentá de nuevo más tarde.',

    // IPv6
    invalid_cidr: 'El CIDR de IPv6 no es válido.',
    invalid_prefix: 'El prefijo debe estar entre 0 y 128.',
    zone_id_not_supported: 'No se admiten identificadores de zona (ej. %eth0).',

    // Módulo 2 (Diagnóstico de conectividad)
    invalid_host: 'El host debe ser una dirección IP o dominio válido.',
    invalid_count: 'La cantidad de paquetes debe ser válida.',
    invalid_max_hops: 'El límite de saltos debe estar entre 1 y 30.',
    invalid_port: 'El puerto debe estar entre 1 y 65535.',
    invalid_timeout: 'El tiempo de espera no es válido.',
    invalid_domain: 'El dominio no es válido.',
    invalid_record_type: 'El tipo de registro DNS no es soportado.',
    invalid_resolver: 'La IP del servidor DNS no es válida.',
    host_unreachable: 'No se pudo resolver el dominio o la red no es alcanzable.',
    ping_timeout: 'La ejecución del ping superó el tiempo límite.',
    traceroute_timeout: 'El trazado tardó demasiado.',
    tcp_timeout: 'La prueba de puerto superó el tiempo límite.',
    dns_timeout: 'El servidor DNS no respondió a tiempo.',
    

    // Módulo 4 (Inventario)
    invalid_name: 'El nombre del dispositivo es obligatorio.',
    invalid_ip: 'La dirección IP no es una IPv4 válida.',
    duplicate_ip: 'Esta dirección IP ya está registrada en el sistema.',
    invalid_status: 'El estado seleccionado no es válido.',
    invalid_mac: 'El formato de la dirección MAC no es válido.',
    invalid_parameter: 'La opción seleccionada no es válida (IP, transporte o túnel).',
    packet_too_small: 'Las cabeceras de red superan el tamaño del MTU.',
    mtu_below_minimum: 'El MTU ingresado es menor al mínimo estándar de IPv4 (576 bytes).',

    // Errores comunes de ejecución (Módulo 2 y 3)
    execution_failed: 'No se pudo ejecutar la herramienta del sistema operativo.',
    too_many_requests: 'Demasiadas solicitudes simultáneas. Esperá unos segundos.',

    // Módulo 5 (Inventario)

    missing_title: 'El título del informe es obligatorio.',
    empty_findings: 'El informe debe contener al menos un hallazgo.',
    missing_finding_fields: 'Todos los hallazgos deben tener un paso y un resultado.',
    invalid_symptom: 'El síntoma seleccionado no existe en el catálogo.',
    empty_configs: 'Al menos una de las configuraciones debe tener contenido.',
    invalid_command_type: 'El comando seleccionado no es válido o no está soportado.',
    missing_target: 'Este comando requiere que ingreses un objetivo (IP o dominio).',
    invalid_target: 'El objetivo debe ser una dirección IP o un dominio válido.',
    invalid_option: 'Una de las opciones seleccionadas no es válida para este comando.',
  };

  const detailCodes = new Set([
    // Módulo 1
    'invalid_json', 'invalid_body', 'unknown_field', 'incompatible_inputs',
    'missing_field', 'invalid_type', 'invalid_value', 'non_contiguous_netmask',
    'insufficient_capacity', 'validation_error', 'unsupported_media_type',
    // IPv6
    'invalid_cidr', 'invalid_prefix', 'zone_id_not_supported',
    // Módulo 2
    'invalid_host', 'invalid_count', 'invalid_max_hops', 'invalid_port', 
    'invalid_timeout', 'invalid_domain', 'invalid_record_type', 'invalid_resolver',
    'host_unreachable', 'ping_timeout', 'traceroute_timeout', 'tcp_timeout', 'dns_timeout',
    // Módulo 4
    'invalid_name', 'invalid_ip',
    'duplicate_ip', 'invalid_status',
    'invalid_mac',
    'invalid_parameter', 'packet_too_small', 'mtu_below_minimum',
    // Módulo 5
    'missing_title', 'empty_findings', 'missing_finding_fields',
    'invalid_symptom','empty_configs',
    'invalid_command_type','missing_target','invalid_target','invalid_option','not_found',

    // Sistema
    'execution_failed', 'too_many_requests'
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
    if (response?.status === 429) return messages.too_many_requests;
    if (response?.status >= 500) return messages.internal_error;
    return 'No se pudo completar la solicitud. Revisá los datos e intentá de nuevo.';
  }

  function title(response) {
    if (response?.status === 415) return 'Formato no admitido';
    if (response?.status === 422) return 'Revisá los datos';
    if (response?.status === 429) return 'Demasiadas solicitudes';
    if (response?.status >= 500) return 'Error del servidor';
    return 'No se pudo completar';
  }

  window.NetOpsApiErrors = { message, title };
})();