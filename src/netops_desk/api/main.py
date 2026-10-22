"""Punto de entrada de la aplicación FastAPI de NetOps Desk.

Crea la aplicación, registra los handlers de excepciones y monta los
routers y los archivos estáticos.

Los handlers de excepciones viven en netops_desk.api.exceptions: este
módulo solo se encarga de registrarlos en el orden correcto.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from netops_desk.api.exceptions import (
    APIValidationError,
    api_validation_error_handler,
    domain_error_handler,
    general_exception_handler,
    http_exception_handler,
    pydantic_validation_error_handler,
)

from netops_desk.api.routes.subnetting import router as subnetting_router
from netops_desk.api.routes.ipv4 import router as ipv4_router
from netops_desk.ipv4 import DomainError
from netops_desk.api.routes.vlsm import router as vlsm_router
from netops_desk.api.routes.overlap import router as overlap_router
from netops_desk.api.routes.ipv6 import router as ipv6_router
from netops_desk.api.routes.ping import router as ping_router
from netops_desk.api.routes.traceroute import router as traceroute_router
from netops_desk.api.routes.tcp_test import router as tcp_test_router
from netops_desk.api.routes.dns_test import router as dns_test_router
from netops_desk.api.routes.route_analyzer import router as route_analyzer_router
from netops_desk.api.routes.interfaces import router as interfaces_router
from netops_desk.api.routes.ip_config import router as ip_config_router
from netops_desk.api.routes.arp_viewer import router as arp_viewer_router
from netops_desk.api.routes.route_table import router as route_table_router
from netops_desk.api.routes.adapters import router as adapters_router
from netops_desk.api.routes.inventory import router as inventory_router
from netops_desk.api.routes.ipam import router as ipam_router
from netops_desk.api.routes.mac_analyzer import router as mac_analyzer_router
from netops_desk.api.routes.port_catalog import router as port_catalog_router
from netops_desk.api.routes.mtu_calculator import router as mtu_calculator_router
from netops_desk.api.routes.report_generator import router as report_generator_router
from netops_desk.api.routes.troubleshooter import router as troubleshooter_router
from netops_desk.api.routes.config_comparator import router as config_comparator_router
from netops_desk.api.routes.command_generator import router as command_generator_router
from netops_desk.api.routes.history import router as history_router
from netops_desk.api.dependencies import get_current_user
from netops_desk.api.routes.auth import router as auth_router


# Auth 
dependencies = [Depends(get_current_user)]

# Directorio donde viven los archivos estáticos (HTML, CSS, JS).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"



def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI.

    Usa el patrón factory para poder instanciar la app en tests con
    distinta configuración si hiciera falta.
    """
    app = FastAPI(
        title="NetOps Desk API",
        description="Herramientas de red para soporte IT.",
        version="0.1.0",
    )

    # Registramos los handlers de excepciones.
    # El orden importa: los más específicos primero, los generales al final.
    # FastAPI evalúa el tipo de excepción para elegir el handler adecuado.
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(APIValidationError, api_validation_error_handler)
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.middleware("http")
    async def prevent_stale_auth_assets(request, call_next):
        response = await call_next(request)
        if request.url.path in {
            "/",
            "/login",
            "/static/js/common.js",
            "/static/js/login.js",
            "/static/js/auth.js",
        }:
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    
    # Routers de la API.
    app.include_router(ipv4_router, dependencies=dependencies)         # calc. ikpv4
    app.include_router(subnetting_router, dependencies=dependencies)   # calc. subnetting
    app.include_router(vlsm_router, dependencies=dependencies)         # calc. vlsm
    app.include_router(overlap_router, dependencies=dependencies)
    app.include_router(ipv6_router, dependencies=dependencies)
    app.include_router(ping_router, dependencies=dependencies)
    app.include_router(traceroute_router, dependencies=dependencies)
    app.include_router(tcp_test_router, dependencies=dependencies)
    app.include_router(dns_test_router, dependencies=dependencies)
    app.include_router(route_analyzer_router, dependencies=dependencies)
    app.include_router(interfaces_router, dependencies=dependencies)
    app.include_router(ip_config_router, dependencies=dependencies)
    app.include_router(arp_viewer_router, dependencies=dependencies)
    app.include_router(route_table_router, dependencies=dependencies)
    app.include_router(adapters_router, dependencies=dependencies)
    app.include_router(inventory_router, dependencies=dependencies)
    app.include_router(ipam_router, dependencies=dependencies)
    app.include_router(mac_analyzer_router, dependencies=dependencies)
    app.include_router(port_catalog_router, dependencies=dependencies)
    app.include_router(mtu_calculator_router, dependencies=dependencies)
    app.include_router(report_generator_router, dependencies=dependencies)
    app.include_router(troubleshooter_router, dependencies=dependencies)
    app.include_router(config_comparator_router, dependencies=dependencies)
    app.include_router(command_generator_router, dependencies=dependencies)
    app.include_router(history_router, dependencies=dependencies)
    app.include_router(auth_router)


    # Archivos estáticos. Se monta DESPUÉS del router para no interceptar
    # las rutas /api/*; el prefijo /static es explícito para que no colisione
    # con la ruta raíz.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def root() -> FileResponse:
        """Sirve el index.html de la aplicación en la ruta raíz."""
        return FileResponse(STATIC_DIR / "index.html")
        # --- Rutas de Páginas (Frontend) ---
    
    # Agregamos la ruta para el login.html
    @app.get("/login", include_in_schema=False)
    async def login_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "login.html")

    # Agregamos la ruta para los modulos
    @app.get("/modulo-1", include_in_schema=False)
    async def modulo_1_page() -> FileResponse:
        # Le agregamos la carpeta "modules" a la ruta
        return FileResponse(STATIC_DIR / "modules" / "modulo-1.html")
    
    @app.get("/modulo-2", include_in_schema=False)
    async def modulo_2_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "modules" / "modulo-2.html")
        
    @app.get("/modulo-3", include_in_schema=False)
    async def modulo_3_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "modules" / "modulo-3.html")

    @app.get("/modulo-4", include_in_schema=False)
    async def modulo_4_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "modules" / "modulo-4.html")
    
    @app.get("/modulo-5", include_in_schema=False)
    async def modulo_5_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "modules" / "modulo-5.html")
    
    # Agregamos la ruta para las tools

    # Agregamos la ruta para la calculadora de IPv4
    @app.get("/tools/ipv4", include_in_schema=False)
    async def ipv4_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "ipv4.html")
    # Agregamos la ruta para subnetting
    @app.get("/tools/subnetting", include_in_schema=False)
    async def subnetting_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "subnetting.html")

    # Agregamos la ruta para vlsm
    @app.get("/tools/vlsm", include_in_schema=False)
    async def vlsm_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "vlsm.html")

    # Agregamos la ruta para overlap
    @app.get("/tools/overlap", include_in_schema=False)
    async def overlap_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "overlap.html")

    @app.get("/tools/ipv6", include_in_schema=False)
    async def ipv6_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "ipv6.html")
    
    @app.get("/tools/ping", include_in_schema=False)
    async def ping_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "ping.html")
    
    @app.get("/tools/traceroute", include_in_schema=False)
    async def traceroute_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "traceroute.html")
    
    @app.get("/tools/tcp-test", include_in_schema=False)
    async def tcp_test_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "tcp-test.html")
    
    @app.get("/tools/dns-test", include_in_schema=False)
    async def dns_test_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "dns-test.html")
    
    @app.get("/tools/route-analyzer", include_in_schema=False)
    async def route_analyzer_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "route-analyzer.html")
    
    @app.get("/tools/interfaces", include_in_schema=False)
    async def interfaces_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "interfaces.html")

    @app.get("/tools/ip-config", include_in_schema=False)
    async def ip_config_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "ip-config.html")
 
    @app.get("/tools/arp-viewer", include_in_schema=False)
    async def arp_viewer_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "arp-viewer.html")
    
    @app.get("/tools/route-table", include_in_schema=False)
    async def route_table_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "route-table.html")
    
    @app.get("/tools/adapters", include_in_schema=False)
    async def adapters_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "adapters.html")

    @app.get("/tools/inventory", include_in_schema=False)
    async def inventory_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "inventory.html")
    
    @app.get("/tools/ipam", include_in_schema=False)
    async def ipam_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "ipam.html")
 
    @app.get("/tools/mac-analyzer", include_in_schema=False)
    async def mac_analyzer_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "mac-analyzer.html")

    @app.get("/tools/port-catalog", include_in_schema=False)
    async def port_catalog_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "port-catalog.html")

    @app.get("/tools/mtu-calculator", include_in_schema=False)
    async def mtu_calculator_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "mtu-calculator.html")

    @app.get("/tools/report-generator", include_in_schema=False)
    async def report_generator_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "report-generator.html")

    @app.get("/tools/troubleshooter", include_in_schema=False)
    async def troubleshooter_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "troubleshooter.html")
    
    @app.get("/tools/config-comparator", include_in_schema=False)
    async def config_comparator_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "config-comparator.html")

    @app.get("/tools/command-generator", include_in_schema=False)
    async def command_generator_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "command-generator.html")

    @app.get("/tools/history", include_in_schema=False)
    async def history_tool_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "tools" / "history.html")

    return app
    
# Instancia que Uvicorn importa: 'netops_desk.api.main:app'.
app = create_app()
