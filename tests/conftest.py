"""Fixtures compartidos para las pruebas de API."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.dependencies import get_current_user
from netops_desk.api.main import app as global_app, create_app


def _fake_runner_for_module(app, module) -> None:
    """Inyecta el runner falso definido por el módulo de prueba, si existe."""
    name = module.__name__.rsplit(".", maxsplit=1)[-1]
    runner_specs = {
        "test_api_adapters": ("netops_desk.api.routes.adapters", "get_adapters_runner", "FakeRunner", ()),
        "test_api_arp_viewer": ("netops_desk.api.routes.arp_viewer", "get_arp_runner", "FakeArpRunner", ()),
        "test_api_dns_test": ("netops_desk.api.routes.dns_test", "get_dns_runner", "FakeRunner", ()),
        "test_api_interfaces": ("netops_desk.api.routes.interfaces", "get_interfaces_runner", "FakeRunner", ()),
        "test_api_mac_analyzer": ("netops_desk.api.routes.mac_analyzer", "get_mac_runner", "FakeRunner", ()),
        "test_api_ping": (
            "netops_desk.api.routes.ping",
            "get_ping_runner",
            "FakeRunner",
            ("Reply from 8.8.8.8: bytes=32 time=12ms TTL=117\n",),
        ),
        "test_api_route_table": ("netops_desk.api.routes.route_table", "get_route_table_runner", "FakeRunner", ()),
        "test_api_router_analyzer": ("netops_desk.api.routes.route_analyzer", "get_route_runner", "FakeRunner", ()),
        "test_api_tcp_test": ("netops_desk.api.routes.tcp_test", "get_tcp_runner", "FakeTcpRunner", ()),
        "test_api_traceroute": (
            "netops_desk.api.routes.traceroute",
            "get_traceroute_runner",
            "FakeRunner",
            ("Tracing route to 8.8.8.8\n  1     1 ms     1 ms     1 ms  192.168.1.1\n",),
        ),
    }
    spec = runner_specs.get(name)
    fake_runner = getattr(module, spec[2], None) if spec else None
    if not spec or fake_runner is None:
        return

    import importlib

    dependency = getattr(importlib.import_module(spec[0]), spec[1])
    app.dependency_overrides[dependency] = lambda: fake_runner(*spec[3])


@pytest.fixture
def app(request):
    """Aplicación nueva con autenticación y runners aislados para cada test."""
    test_app = create_app()
    test_app.dependency_overrides[get_current_user] = lambda: {
        "sub": "testuser",
        "role": "admin",
    }
    _fake_runner_for_module(test_app, request.module)

    module_name = request.module.__name__.rsplit(".", maxsplit=1)[-1]
    repository_specs = {
        "test_api_history": (
            "netops_desk.api.routes.history",
            "get_history_repo",
            "netops_desk.repositories.history_repository",
            "SQLiteHistoryRepository",
        ),
        "test_api_inventory": (
            "netops_desk.api.routes.inventory",
            "get_inventory_repo",
            "netops_desk.repositories.inventory_repository",
            "SQLiteInventoryRepository",
        ),
        "test_api_ipam": (
            "netops_desk.api.routes.ipam",
            "get_ipam_repo",
            "netops_desk.repositories.ipam_repository",
            "SQLiteIpamRepository",
        ),
    }
    repository_spec = repository_specs.get(module_name)
    if repository_spec:
        import importlib

        route_module = importlib.import_module(repository_spec[0])
        repository_module = importlib.import_module(repository_spec[2])
        repository = getattr(repository_module, repository_spec[3])(db_path=":memory:")
        test_app.dependency_overrides[getattr(route_module, repository_spec[1])] = (
            lambda: repository
        )
    return test_app


@pytest.fixture
def client(app):
    """Cliente autenticado de la aplicación del test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def authenticate_module_level_app():
    """Autentica clientes creados al importar módulos de pruebas históricos."""
    global_app.dependency_overrides[get_current_user] = lambda: {
        "sub": "testuser",
        "role": "admin",
    }
    yield
    global_app.dependency_overrides.pop(get_current_user, None)
