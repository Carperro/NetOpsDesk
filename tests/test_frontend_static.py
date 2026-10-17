"""Pruebas estaticas del frontend servido desde FastAPI."""

from __future__ import annotations

from fastapi.testclient import TestClient
from netops_desk.api.main import app


client = TestClient(app)


def test_root_returns_index_html():
    """GET / devuelve el dashboard con tema claro inicial."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert 'lang="es"' in html
    assert 'data-theme="light"' in html
    assert "<title>NetOps Desk - Inicio</title>" in html
    assert 'href="/tools/ipv4"' in html


def test_html_contains_three_operation_forms():
    """La página de la calculadora conserva sus tres formularios."""
    response = client.get("/tools/ipv4")
    assert response.status_code == 200
    html = response.text
    for element_id in (
        "form-direct-cidr",
        "form-direct-address",
        "form-inverse",
        "cidr",
        "address",
        "netmask",
        "required-hosts",
        "mode-direct-cidr",
        "mode-direct-address",
        "mode-inverse",
    ):
        assert f'id="{element_id}"' in html


def test_html_references_reset_and_styles_in_order():
    """La calculadora referencia sus CSS bajo /static/css en orden."""
    html = client.get("/tools/ipv4").text
    reset_pos = html.find('/static/css/reset.css')
    styles_pos = html.find('/static/css/styles.css')
    assert reset_pos != -1, "Falta referencia a /static/css/reset.css"
    assert styles_pos != -1, "Falta referencia a /static/css/styles.css"
    assert reset_pos < styles_pos, "reset.css debe cargarse antes que styles.css"


def test_sidebar_script_defines_theme_and_logout_controls():
    """El sidebar inyecta los controles de tema y cierre de sesión."""
    response = client.get("/static/js/sidebar.js")
    assert response.status_code == 200
    sidebar_js = response.text
    assert 'id="theme-toggle"' in sidebar_js
    assert 'id="logout-btn"' in sidebar_js
    assert "getElementById('sidebar-container')" in sidebar_js


def test_static_reset_css_served():
    """GET /static/css/reset.css devuelve un recurso CSS."""
    response = client.get("/static/css/reset.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert response.content


def test_static_styles_css_served():
    """GET /static/css/styles.css devuelve un recurso CSS."""
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert response.content


def test_static_ipv4_js_served():
    """GET /static/js/ipv4.js devuelve el controlador de la calculadora."""
    response = client.get("/static/js/ipv4.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert response.content


def test_static_common_js_served():
    """GET /static/js/common.js devuelve las utilidades compartidas."""
    response = client.get("/static/js/common.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert response.content


def test_api_still_works():
    """Una solicitud directa valida conserva el contrato de la API."""
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.168.1.0"
    assert data["broadcast"] == "192.168.1.255"
    assert data["netmask"] == "255.255.255.0"
    assert data["total_addresses"] == 256
    assert data["usable_addresses"] == 254
    assert "binary" in data
    assert "warnings" in data


def test_method_not_allowed_preserved():
    """GET al endpoint de calculo conserva HTTP 405."""
    response = client.get("/api/v1/tools/ipv4/calculate")
    assert response.status_code == 405
    assert response.json()["error"] == "method_not_allowed"


def test_static_files_not_mounted_at_root():
    """Los recursos estaticos no se montan en las rutas raiz."""
    for path in ("/css/reset.css", "/css/styles.css", "/js/ipv4.js"):
        assert client.get(path).status_code == 404


def test_api_405_contractual_preserved():
    """El endpoint conserva 405 antes de validar el cuerpo."""
    response = client.get("/api/v1/tools/ipv4/calculate")
    assert response.status_code == 405
    assert response.json()["error"] == "method_not_allowed"


def test_ipv4_js_covers_all_contractual_error_codes():
    """El JavaScript IPv4 contempla los códigos contractuales de error."""
    js_content = client.get("/static/js/ipv4.js").text
    contractual_codes = (
        "method_not_allowed",
        "unsupported_media_type",
        "invalid_json",
        "invalid_body",
        "unknown_field",
        "incompatible_inputs",
        "missing_field",
        "invalid_type",
        "invalid_value",
        "non_contiguous_netmask",
        "insufficient_capacity",
        "internal_error",
    )
    for code in contractual_codes:
        assert code in js_content, f"Falta el codigo contractual: {code}"


def test_operation_picker_has_three_native_options_and_one_visible_panel():
    """Los radios nativos ofrecen las tres operaciones y una selección inicial."""
    html = client.get("/tools/ipv4").text
    for operation in ("direct-cidr", "direct-address", "inverse"):
        assert f'name="operation" value="{operation}"' in html
    assert 'name="operation" value="direct-cidr" checked' in html
    assert 'id="panel-direct-cidr" class="operation-panel"' in html
    assert 'id="panel-direct-address" class="operation-panel" hidden' in html
    assert 'id="panel-inverse" class="operation-panel" hidden' in html


def test_contractual_form_field_names_and_types_are_preserved():
    """Los campos y modos conservan los nombres y tipos de entrada."""
    html = client.get("/tools/ipv4").text
    assert 'id="cidr" name="cidr"' in html
    assert 'id="address" name="address"' in html
    assert 'id="netmask" name="netmask"' in html
    assert 'type="number" id="required-hosts" name="required_hosts"' in html
    assert html.count('name="mode"') == 3
    assert 'value="conventional"' in html
    assert 'value="point-to-point"' in html


def test_each_operation_has_separate_output_regions():
    """Cada operación tiene regiones propias de resultado, warning y error."""
    html = client.get("/tools/ipv4").text
    for operation in ("direct-cidr", "direct-address", "inverse"):
        assert f'id="result-{operation}" class="result-area"' in html
        assert f'id="warnings-{operation}" class="warning-list"' in html
        assert f'id="error-{operation}" class="error-area"' in html
    assert html.count('class="operation-status" role="status"') == 3


def test_theme_control_is_injected_and_wired_by_shared_scripts():
    """El sidebar crea el control y common.js registra su comportamiento."""
    sidebar_js = client.get("/static/js/sidebar.js").text
    common_js = client.get("/static/js/common.js").text
    assert 'id="theme-toggle"' in sidebar_js
    assert 'id="theme-text"' in sidebar_js
    assert "function initTheme()" in common_js
    assert "function toggleTheme()" in common_js
    assert "themeBtn.addEventListener('click', toggleTheme)" in common_js


def test_warnings_render_code_and_message_without_object_interpolation():
    """El renderer usa los campos code y message del warning."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "warning.code" in js_content
    assert "warning.message" in js_content
    assert "${warning}" not in js_content
    assert "alert__header" in js_content
    assert "alert__message" in js_content


def test_dynamic_api_values_do_not_use_inner_html():
    """Los valores dinamicos se crean como nodos y se asignan como texto."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "innerHTML" not in js_content
    assert "document.createElement" in js_content
    assert "element.textContent = text" in js_content


def test_binary_result_is_collapsible_and_has_six_contractual_fields():
    """El binario se presenta en details y conserva las seis claves."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "makeElement('details', 'binary-details')" in js_content
    assert "Ver representación binaria" in js_content
    for field in ("network", "broadcast", "netmask", "wildcard", "first_usable", "last_usable"):
        assert f"['{field}'," in js_content


def test_null_and_missing_result_values_use_explanatory_text():
    """Los valores nulos o ausentes se explican sin imprimir null o undefined."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "No disponible para este prefijo y modo" in js_content
    assert "value === null || value === undefined" in js_content
    assert "String(value)" in js_content


def test_loading_state_uses_accessible_status_busy_and_disabled_button():
    """El formulario anuncia el estado ocupado y bloquea su boton de envio."""
    html = client.get("/tools/ipv4").text
    js_content = client.get("/static/js/ipv4.js").text
    assert 'role="status" aria-live="polite"' in html
    assert "setAttribute('aria-busy', String(busy))" in js_content
    assert "button.disabled = busy" in js_content
    assert "Calculando…" in js_content


def test_changing_operation_clears_outputs_and_cancels_stale_request():
    """Cambiar de operacion limpia salidas y evita mostrar una respuesta obsoleta."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "function clearAllOutputs()" in js_content
    assert "function cancelActiveRequest()" in js_content
    assert "activeRequest.controller.abort()" in js_content
    assert "panel.hidden = panel.id !== `panel-${operation}`" in js_content
    assert "version !== requestVersion" in js_content


def test_api_errors_and_non_json_responses_have_safe_fallbacks():
    """El renderer conserva mensajes amigables y maneja respuestas inesperadas."""
    js_content = client.get("/static/js/ipv4.js").text
    assert "errorMessages[code]" in js_content
    assert "La solicitud no pudo completarse." in js_content
    assert "La respuesta del servidor no contiene JSON válido." in js_content
    assert "No se pudo conectar con el servidor." in js_content


if __name__ == "__main__":
    pass
