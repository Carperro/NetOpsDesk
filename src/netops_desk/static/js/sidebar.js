/**
 * sidebar.js - Renderiza el menú lateral de forma dinámica
 */
(function () {
    const container = document.getElementById('sidebar-container');
    if (!container) return;

    // Detectamos en qué página estamos para marcar el botón correcto como "activo"
    const path = window.location.pathname;
    const isHome = path === '/';
    const isModulo = path.includes('/modulo') || path.includes('/tools');

    container.innerHTML = `
        <aside class="sidebar">
            <div class="sidebar-header">
                <span class="brand-icon" aria-hidden="true">■</span> NetOps Desk
            </div>

            <nav class="sidebar-nav">
                <a href="/" class="nav-item ${isHome ? 'active' : ''}">Inicio</a>
                <a href="/modulo-1" class="nav-item ${isModulo ? 'active' : ''}">Módulos</a>
                <a href="#" class="nav-item">Favoritos</a>
            </nav>

            <div class="sidebar-footer">
                <button id="theme-toggle" class="nav-item theme-toggle-btn">
                    <span id="theme-icon" aria-hidden="true">◐</span> <span id="theme-text">Modo oscuro</span>
                </button>
                <button id="logout-btn" class="nav-item btn-logout">Cerrar Sesión</button>

                <div class="user-profile">
                    <div class="user-avatar" id="user-avatar">?</div>
                    <div class="user-info">
                        <div id="user-name" class="user-name">Cargando...</div>
                        <div class="user-role">Admin</div>
                    </div>
                </div>
            </div>
        </aside>
    `;
})();