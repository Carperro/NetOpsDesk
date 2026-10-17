"""Pruebas estaticas del frontend servido desde FastAPI."""

from __future__ import annotations

from fastapi.testclient import TestClient
from netops_desk.api.main import app


client = TestClient(app)


def test_root_returns_index_html():
    """GET / devuelve HTML en espanol con tema oscuro inicial."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert 'lang="es"' in html
    assert 'data-theme="dark"' in html
    assert "<title>NetOps Desk \u2014 Calculadora IPv4</title>" in html
    assert "NetOps Desk" in html


def test_html_contains_three_operation_forms():
    """El documento conserva los identificadores de los tres formularios."""
    html = client.get("/").text
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
    """index.html referencia los CSS estaticos en el orden correcto."""
    html = client.get("/").text
    reset_pos = html.find('/static/reset.css')
    styles_pos = html.find('/static/styles.css')
    assert reset_pos != -1, "Falta referencia a /static/reset.css"
    assert styles_pos != -1, "Falta referencia a /static/styles.css"
    assert reset_pos < styles_pos, "reset.css debe cargarse antes que styles.css"


def test_html_has_accessible_theme_toggle():
    """El control inicial de tema declara su estado y accion accesible."""
    html = client.get("/").text
    assert 'id="theme-toggle"' in html
    assert 'aria-pressed="true"' in html
    assert 'aria-label="Cambiar a tema claro"' in html
    assert 'class="theme-toggle__label">Cambiar a tema claro</span>' in html


def test_static_reset_css_served():
    """GET /static/reset.css devuelve un recurso CSS."""
    response = client.get("/static/reset.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert response.content


def test_static_styles_css_served():
    """GET /static/styles.css devuelve un recurso CSS."""
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert response.content


def test_static_app_js_served():
    """GET /static/app.js devuelve un recurso JavaScript."""
    response = client.get("/static/app.js")
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
    for path in ("/reset.css", "/styles.css", "/app.js"):
        assert client.get(path).status_code == 404


def test_api_405_contractual_preserved():
    """El endpoint conserva 405 antes de validar el cuerpo."""
    response = client.get("/api/v1/tools/ipv4/calculate")
    assert response.status_code == 405
    assert response.json()["error"] == "method_not_allowed"


def test_app_js_covers_all_contractual_error_codes():
    """El JavaScript contempla los doce codigos contractuales de error."""
    js_content = client.get("/static/app.js").text
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
    """Los radios relacionan las tres operaciones con sus paneles."""
    html = client.get("/").text
    for operation in ("direct-cidr", "direct-address", "inverse"):
        assert f'name="operation" value="{operation}"' in html
        assert f'aria-controls="panel-{operation}"' in html
    assert 'value="direct-cidr" aria-controls="panel-direct-cidr" checked' in html
    assert 'id="panel-direct-cidr" class="operation-panel"' in html
    assert 'id="panel-direct-address" class="operation-panel" aria-labelledby="direct-address-heading" hidden' in html
    assert 'id="panel-inverse" class="operation-panel" aria-labelledby="inverse-heading" hidden' in html


def test_contractual_form_field_names_and_types_are_preserved():
    """Los campos y modos conservan los nombres y tipos de entrada."""
    html = client.get("/").text
    assert 'id="cidr" name="cidr"' in html
    assert 'id="address" name="address"' in html
    assert 'id="netmask" name="netmask"' in html
    assert 'type="number" id="required-hosts" name="required_hosts"' in html
    assert html.count('name="mode"') == 3
    assert 'value="conventional"' in html
    assert 'value="point-to-point"' in html


def test_each_operation_has_separate_accessible_output_regions():
    """Cada operacion tiene regiones propias de resultado, warning y error."""
    html = client.get("/").text
    for operation in ("direct-cidr", "direct-address", "inverse"):
        assert f'id="result-{operation}" class="result-area" aria-live="polite"' in html
        assert f'id="warnings-{operation}" class="warning-list"' in html
        assert f'id="error-{operation}" class="error-area" role="alert"' in html
    assert html.count('class="operation-status" role="status"') == 3


def test_theme_control_uses_one_text_source_and_syncs_accessible_state():
    """El control evita pseudo texto y sincroniza etiqueta y aria-pressed."""
    html = client.get("/").text
    js_content = client.get("/static/app.js").text
    css_content = client.get("/static/styles.css").text
    assert 'class="theme-toggle__label">Cambiar a tema claro</span>' in html
    assert "setAttribute('aria-label', actionLabel)" in js_content
    assert "setAttribute('aria-pressed', String(isDark))" in js_content
    assert "themeLabel.textContent = actionLabel" in js_content
    assert "theme-toggle[aria-pressed" not in css_content


def test_warnings_render_code_and_message_without_object_interpolation():
    """El renderer usa los campos code y message del warning."""
    js_content = client.get("/static/app.js").text
    assert "warning.code" in js_content
    assert "warning.message" in js_content
    assert "${warning}" not in js_content
    assert "item.append(makeElement('strong'" in js_content
    assert "item.append(makeElement('p'" in js_content


def test_dynamic_api_values_do_not_use_inner_html():
    """Los valores dinamicos se crean como nodos y se asignan como texto."""
    js_content = client.get("/static/app.js").text
    assert "innerHTML" not in js_content
    assert "document.createElement" in js_content
    assert "element.textContent = text" in js_content


def test_binary_result_is_collapsible_and_has_six_contractual_fields():
    """El binario se presenta en details y conserva las seis claves."""
    js_content = client.get("/static/app.js").text
    assert "makeElement('details', 'binary-details')" in js_content
    assert "Ver representación binaria" in js_content
    for field in ("network", "broadcast", "netmask", "wildcard", "first_usable", "last_usable"):
        assert f"['{field}'," in js_content


def test_null_and_missing_result_values_use_explanatory_text():
    """Los valores nulos o ausentes se explican sin imprimir null o undefined."""
    js_content = client.get("/static/app.js").text
    assert "No disponible para este prefijo y modo" in js_content
    assert "value === null || value === undefined" in js_content
    assert "String(value)" in js_content


def test_loading_state_uses_accessible_status_busy_and_disabled_button():
    """El formulario anuncia el estado ocupado y bloquea su boton de envio."""
    html = client.get("/").text
    js_content = client.get("/static/app.js").text
    assert 'role="status" aria-live="polite"' in html
    assert "setAttribute('aria-busy', String(busy))" in js_content
    assert "button.disabled = busy" in js_content
    assert "Calculando…" in js_content


def test_changing_operation_clears_outputs_and_cancels_stale_request():
    """Cambiar de operacion limpia salidas y evita mostrar una respuesta obsoleta."""
    js_content = client.get("/static/app.js").text
    assert "function clearAllOutputs()" in js_content
    assert "function cancelActiveRequest()" in js_content
    assert "activeRequest.controller.abort()" in js_content
    assert "panel.hidden = panel.id !== `panel-${operation}`" in js_content
    assert "version !== requestVersion" in js_content


def test_api_errors_and_non_json_responses_have_safe_fallbacks():
    """El renderer conserva mensajes amigables y maneja respuestas inesperadas."""
    js_content = client.get("/static/app.js").text
    assert "errorMessages[code]" in js_content
    assert "La solicitud no pudo completarse." in js_content
    assert "La respuesta del servidor no contiene JSON válido." in js_content
    assert "No se pudo conectar con el servidor." in js_content


if __name__ == "__main__":
    pass
