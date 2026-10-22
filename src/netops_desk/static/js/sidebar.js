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
            <a href="/" class="sidebar-brand" title="Ir al inicio">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="brand-logo-svg">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    <circle cx="12" cy="10" r="2.5"></circle>
                    <path d="M12 12.5v4"></path>
                    <path d="M9.5 9H6"></path>
                    <path d="M14.5 9h3.5"></path>
                </svg>
                <span class="brand-text">NetOps Desk</span>
            </a>
            <button type="button" class="sidebar-close" aria-label="Cerrar menú">×</button>       

            <nav class="sidebar-nav">
                <a href="/" class="nav-item ${isHome ? 'active' : ''}">Inicio</a>
                <a href="/modulo-1" class="nav-item ${isModulo ? 'active' : ''}">Módulos</a>
                <a href="/?favorites=1" class="nav-item">Favoritos</a>
            </nav>

            <div class="sidebar-footer">
                <button id="theme-toggle" class="nav-item theme-toggle-btn">
                    <span id="theme-icon" aria-hidden="true">◐</span> <span id="theme-text">Modo oscuro</span>
                </button>
                <button id="logout-btn" data-logout class="nav-item btn-logout">Cerrar Sesión</button>

                <div class="user-profile">
                    <div class="user-avatar" id="user-avatar" aria-hidden="true">A</div>
                    <div class="user-info">
                        <div id="user-name" class="user-name">Cargando...</div>
                        <div class="user-role" id="user-role">Usuario</div>
                    </div>
                </div>
            </div>
        </aside>
    `;

    const logoutButton = container.querySelector("[data-logout]");
    logoutButton?.addEventListener("click", () => {
        localStorage.removeItem("netops_token");
        localStorage.removeItem("netops_user");
        window.location.replace("/login");
    });

    const sidebar = container.querySelector(".sidebar");
    const topbar = document.querySelector(".topbar");
    if (sidebar && topbar) {
        sidebar.id = "app-sidebar";

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "mobile-menu-toggle";
        toggle.textContent = "☰";
        toggle.setAttribute("aria-label", "Abrir menú");
        toggle.setAttribute("aria-haspopup", "true");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-controls", sidebar.id);

        const backdrop = document.createElement("button");
        backdrop.type = "button";
        backdrop.className = "sidebar-backdrop";
        backdrop.setAttribute("aria-label", "Cerrar menú");
        backdrop.hidden = true;
        document.body.append(backdrop);

        const setMenuOpen = (isOpen) => {
            sidebar.classList.toggle("is-open", isOpen);
            backdrop.hidden = !isOpen;
            document.body.classList.toggle("sidebar-open", isOpen);
            toggle.setAttribute("aria-expanded", String(isOpen));
            toggle.setAttribute("aria-label", isOpen ? "Cerrar menú" : "Abrir menú");
            toggle.textContent = isOpen ? "×" : "☰";
            if (isOpen) sidebar.querySelector(".sidebar-close")?.focus();
            else toggle.focus();
        };

        sidebar.querySelector(".sidebar-close")?.addEventListener("click", () => setMenuOpen(false));
        toggle.addEventListener("click", () => {
            setMenuOpen(toggle.getAttribute("aria-expanded") !== "true");
        });
        backdrop.addEventListener("click", () => setMenuOpen(false));
        sidebar.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => setMenuOpen(false));
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
                setMenuOpen(false);
            }
        });

        topbar.prepend(toggle);
    }
})();
